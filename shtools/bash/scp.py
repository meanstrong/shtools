# -*- coding: utf-8 -*-
from optparse import OptionParser

import paramiko

from .ssh import Ssh


class Scp(Ssh):
    def get_parser(self):
        parser = OptionParser(usage="scp [options...] [[user@]host1:]file1 [[user@]host2:]file2")
        parser.add_option(
            "-P",
            action="store",
            type="int",
            dest="port",
            default=22,
            help="Specifies the port to connect to on the remote host.",
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
        options, args = self.parser.parse_args(args)

        if len(args) != 2:
            raise Exception("usage: scp [options] src dst.")
        if ":" in args[0]:
            options.mode = "GET"
            ssh, options.src = args[0].split(":")
            options.dst = args[1]
            if "@" in ssh:
                options.login_name, options.hostname = ssh.split("@")
            else:
                if options.login_name is None:
                    options.login_name = "root"
                options.hostname = ssh
        elif ":" in args[1]:
            options.mode = "PUT"
            options.src = args[0]
            ssh, options.dst = args[1].split(":")
            if "@" in ssh:
                options.login_name, options.hostname = ssh.split("@")
            else:
                if options.login_name is None:
                    options.login_name = "root"
                options.hostname = ssh
        else:
            raise Exception("cannot find any ssh command.")
        return options, args

    def run(self):
        self.connect()
        sftp = paramiko.SFTPClient.from_transport(self.transport)
        if self.options.mode == "GET":
            sftp.get(self.options.src, self.options.dst)
        else:
            sftp.put(self.options.src, self.options.dst)
        self.transport.close()
        self.client.close()
        return
