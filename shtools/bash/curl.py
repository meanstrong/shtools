# -*- coding: utf-8 -*-
from optparse import OptionParser

import requests

from .abstract_cmd import AbstractCmd


__all__ = ["curl"]

parser = OptionParser(usage="curl [options...] <url>")
parser.add_option("-d", "--data", action="store", dest="data", default=None, help="(HTTP) Sends the specified data in a POST request to the HTTP server")
parser.add_option("-H", "--header", action="store", dest="header", default=None, help="(HTTP) Extra header to use when getting a web page.")
parser.add_option("-I", "--head", action="store_true", dest="head", default=False, help="Show document info only.")
parser.add_option(
    "-k",
    "--insecure",
    action="store_true",
    dest="insecure",
    default=False,
    help='(SSL) This option explicitly allows curl to perform "insecure" SSL connections and transfers.',
)
parser.add_option("-m", "--max-time", action="store", type="int", dest="timeout", default=30, help="Maximum time allowed for the transfer")
parser.add_option("-o", "--output", action="store", dest="output", default=None, help="Write output to <file> instead of stdout.")
parser.add_option("-u", "--user", action="store", dest="user", default=None, help="Specify the user name and password to use for server authentication.")
parser.add_option("-x", "--proxy", action="store", dest="proxy", default=None, help="Use the specified HTTP proxy.")
parser.add_option(
    "-X",
    "--request",
    action="store",
    dest="request",
    default="GET",
    help="(HTTP)  Specifies  a  custom  request  method  to  use when communicating with the HTTP server.",
)


class Result(object):
    def __init__(self, status_code: int, content: bytes):
        self._status_code = status_code
        self._content = content

    @property
    def status_code(self):
        return self._status_code

    @property
    def content(self):
        return self._content

    def __str__(self):
        return f"<Response [{self._status_code}]>"


class curl(AbstractCmd):
    __option_parser__ = parser

    def run(self):
        headers = None
        if self.options.header:
            headers = dict(s.strip().split(": ") for s in self.options.header.split(";"))
        resp = requests.request(
            self.options.request,
            self.args[0],
            data=self.options.data,
            headers=headers,
            auth=self.options.user,
            timeout=self.options.timeout,
            proxies=dict(http=self.options.proxy, https=self.options.proxy),
            verify=not self.options.insecure,
        )
        if self.options.output is not None:
            with open(self.options.output, "wb") as f:
                f.write(resp.content)
        return Result(status_code=resp.status_code, content=resp.content)
