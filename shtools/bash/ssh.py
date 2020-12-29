# -*- coding: utf-8 -*-
import socket
import time
from optparse import OptionParser

import paramiko

from .bash import Bash


class Ssh(Bash):
    def get_parser(self):
        parser = OptionParser(usage="ssh [options...] [user@]hostname [command]")
        parser.add_option(
            "-l",
            action="store",
            dest="login_name",
            default=None,
            help="Specifies the user to log in as on the remote machine.",
        )
        parser.add_option(
            "-p", action="store", type="int", dest="port", default=22, help="Port to connect to on the remote host.",
        )
        parser.add_option(
            "--password",
            action="store",
            type="string",
            dest="password",
            default=None,
            help="Specifies the password to connect to on the remote host.",
        )
        return parser

    def parse_args(self, args):
        options, args = super().parse_args(args)
        if "@" in args[0]:
            options.login_name, options.hostname = args[0].split("@")
        else:
            if options.login_name is None:
                options.login_name = "root"
            options.hostname = args[0]
        if len(args) <= 1:
            args = ""
        elif len(args) == 2:
            args = args[1]
        else:
            args = " ".join(args[1:])
        return options, args

    def run(self):
        try:
            self.connect()
            result = self.execute(self.args)
            self.transport.close()
            self.client.close()
        except (socket.error, socket.gaierror) as err:
            self.logger.warn(err)
            # return dict(error="Connection timed out")
            raise
        except paramiko.ssh_exception.NoValidConnectionsError as err:
            self.logger.warn(err)
            # return dict(error="Connection refused")
            raise
        except paramiko.ssh_exception.AuthenticationException as err:
            self.logger.warn(err)
            # return dict(error="Permission denied (Authentication failed.).")
            raise
        # except Exception as err:
        #     print(type(err))
        #     self.logger.exception(err)
        #     return "", str(err), 1
        return result

    def connect(self):
        self.logger.info("Attempting connection to {} via SSH".format(self.options.hostname))

        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(
            hostname=self.options.hostname,
            port=self.options.port,
            username=self.options.login_name,
            password=self.options.password,
        )
        # private_key = paramiko.RSAKey.from_private_key_file('/root/.ssh/id_rsa')
        # ssh.connect(hostname='10.0.3.56', port=22, username='root', pkey=private_key)

        self.logger.info("Connection to node {} established.".format(self.options.hostname))
        self.client = client
        self.transport = self.client.get_transport()

    def sshJump(self, jumpInfo):
        transport = self.client.get_transport()
        dst_address = (jumpInfo["hostname"], jumpInfo.get("port", 22))
        src_address = transport.getpeername()

        self.logger.info("Attempting connection to {} via SSH from {}".format(dst_address[0], src_address[0]))

        new_channel = transport.open_channel("direct-tcpip", dst_address, src_address)
        new_client = paramiko.SSHClient()
        new_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        new_client.connect(
            hostname=jumpInfo["hostname"],
            port=jumpInfo.get("port", 22),
            username=jumpInfo["username"],
            password=jumpInfo["password"],
            sock=new_channel,
        )

        self.logger.info("Connection to node {} established.".format(jumpInfo["hostname"]))
        self.client = new_client
        self.transport = self.client.get_transport()

    def execute(self, command):
        self.logger.info("Execute command <{}>".format(command))
        channel = self.client.get_transport().open_session()
        channel.exec_command(command)
        result = self.refreshBuffer(channel)
        return result

    def getChannel(self):
        channel = self.client.get_transport().open_session()
        # channel.invoke_shell()
        # channel.get_pty()
        # channel.settimeout(None)
        # channel.set_combine_stderr(True)
        return channel

    @staticmethod
    def refreshBuffer(channel, timeout=0.1, bufsize=65535):
        stdout = stderr = ""
        while not channel.exit_status_ready():
            time.sleep(timeout)
            if channel.recv_ready():
                stdout += channel.recv(bufsize).decode("utf-8")
            if channel.recv_stderr_ready():
                stderr += channel.recv_stderr(bufsize).decode("utf-8")
        rc = channel.recv_exit_status()
        # Need to gobble up any remaining output after program terminates...
        while channel.recv_ready():
            stdout += channel.recv(bufsize).decode("utf-8")
        while channel.recv_stderr_ready():
            stderr += channel.recv_stderr(bufsize).decode("utf-8")
        return dict(rc=rc, stdout=stdout, stderr=stderr)

    def transportFile(self, download, upload):
        sftp = paramiko.SFTPClient.from_transport(self.transport)

        if download is not None:
            sftp.get(download["src"], download["dst"])
            self.logger.info("Download Complete")
        else:
            pass

        if upload is not None:
            sftp.put(upload["src"], upload["dst"])
            self.logger.info("Upload Complete")
        else:
            pass
