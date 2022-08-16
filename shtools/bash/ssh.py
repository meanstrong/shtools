# -*- coding: utf-8 -*-
import time
from optparse import OptionParser

import paramiko

from .abstract_cmd import AbstractCmd

__all__ = ["ssh"]

parser = OptionParser(usage="ssh [options...] [user@]hostname [command]")
parser.add_option(
    "-l",
    action="store",
    dest="login_name",
    default=None,
    help="Specifies the user to log in as on the remote machine.",
)
parser.add_option(
    "-p",
    action="store",
    type="int",
    dest="port",
    default=22,
    help="Port to connect to on the remote host.",
)
parser.add_option(
    "--password",
    action="store",
    type="string",
    dest="password",
    default=None,
    help="Specifies the password to connect to on the remote host.",
)


class Result(object):
    def __init__(self, exit_code: int, stdout: bytes = b"", stderr: bytes = b""):
        self._exit_code = exit_code
        self._stdout = stdout
        self._stderr = stderr

    @property
    def exit_code(self):
        return self._exit_code

    @property
    def stdout(self):
        return self._stdout

    @property
    def stderr(self):
        return self._stderr


class ssh(AbstractCmd):
    __option_parser__ = parser

    def _parse_args(self, cmdline):
        options, args = super()._parse_args(cmdline)
        if len(args) > 0:
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
        self.connect()
        result = self.execute(self.args)
        self.transport.close()
        self.client.close()
        return result

    def connect(self):
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

        self.client = client
        self.transport = self.client.get_transport()

    def close(self):
        self.transport.close()
        self.client.close()

    def sshJump(self, jumpInfo):
        transport = self.client.get_transport()
        dst_address = (jumpInfo["hostname"], jumpInfo.get("port", 22))
        src_address = transport.getpeername()

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

        self.client = new_client
        self.transport = self.client.get_transport()

    def execute(self, command):
        channel = self.getChannel()
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
    def refreshBuffer(channel: paramiko.Channel, timeout=0.1, bufsize=65535):
        stdout = stderr = b""
        while not channel.exit_status_ready():
            time.sleep(timeout)
            if channel.recv_ready():
                stdout += channel.recv(bufsize)
            if channel.recv_stderr_ready():
                stderr += channel.recv_stderr(bufsize)
        exit_code = channel.recv_exit_status()
        # Need to gobble up any remaining output after program terminates...
        while channel.recv_ready():
            stdout += channel.recv(bufsize)
        while channel.recv_stderr_ready():
            stderr += channel.recv_stderr(bufsize)
        return Result(exit_code=exit_code, stdout=stdout, stderr=stderr)

    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.close()
