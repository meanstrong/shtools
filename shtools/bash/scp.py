# -*- coding: utf-8 -*-
from optparse import OptionParser

import paramiko

from .ssh import ssh
from shtools.utils.cmdline import CmdLine

__all__ = ["scp"]

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


class scp(ssh):
    __option_parser__ = parser

    def _parse_args(self, cmdline):
        options, args = self.__option_parser__.parse_args(self._get_args(cmdline))

        if len(args) != 2 or sum([1 for arg in args if ":" in arg]) == 1:
            raise Exception(parser.get_usage())
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
        return options, args

    def run(self):
        sftp = paramiko.SFTPClient.from_transport(self.transport)
        if self.options.mode == "GET":
            sftp.get(self.options.src, self.options.dst)
        else:
            sftp.put(self.options.src, self.options.dst)
