# -*- coding: utf-8 -*-
from optparse import OptionParser

import requests

from .bash import Bash


class Curl(Bash):
    def __init__(self, cmdline=""):
        super().__init__(cmdline)
        if self.options.header:
            self.options.header = dict(s.split(": ") for s in self.options.header.split(";"))

    def get_parser(self):
        parser = OptionParser(usage="curl [options...] <url>")
        parser.add_option(
            "-d",
            "--data",
            action="store",
            dest="data",
            default=None,
            help="(HTTP) Sends the specified data in a POST request to the HTTP server",
        )
        parser.add_option(
            "-H",
            "--header",
            action="store",
            dest="header",
            default={},
            help="(HTTP) Extra header to use when getting a web page.",
        )
        parser.add_option(
            "-I", "--head", action="store_true", dest="head", default=False, help="Show document info only."
        )
        parser.add_option(
            "-k",
            "--insecure",
            action="store_true",
            dest="insecure",
            default=False,
            help='(SSL) This option explicitly allows curl to perform "insecure" SSL connections and transfers.',
        )
        parser.add_option(
            "-o",
            "--output",
            action="store",
            dest="output",
            default=None,
            help="Write output to <file> instead of stdout.",
        )
        parser.add_option(
            "-u",
            "--user",
            action="store",
            dest="user",
            default=None,
            help="Specify the user name and password to use for server authentication.",
        )
        parser.add_option(
            "-x", "--proxy", action="store", dest="proxy", default=None, help="Use the specified HTTP proxy."
        )
        parser.add_option(
            "-X",
            "--request",
            action="store",
            dest="request",
            default="GET",
            help="(HTTP)  Specifies  a  custom  request  method  to  use when communicating with the HTTP server.",
        )
        return parser

    def run(self):
        resp = requests.request(
            self.options.request,
            self.args[0],
            data=self.options.data,
            headers=self.options.header,
            auth=self.options.user,
            proxies=dict(http=self.options.proxy, https=self.options.proxy),
            verify=not self.options.insecure,
        )
        return dict(status_code=resp.status_code, text=resp.text)
