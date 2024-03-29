# -*- coding:utf-8 -*-
from optparse import OptionParser

import pymongo

from .abstract_cmd import AbstractCmd

__all__ = ["mongo"]

parser = OptionParser(usage="mongo [options...] [command]")
parser.add_option("--port", action="store", type="int", dest="port", default=27017, help="port to connect to")
parser.add_option("--host", action="store", dest="host", default="127.0.0.1", help="server to connect to")
parser.add_option("-u", "--username", action="store", dest="username", default=None, help="username for authentication")
parser.add_option("-p", "--password", action="store", dest="password", default=None, help="password for authentication")
parser.add_option("--database", action="store", dest="database", default="", help="database")

class Result(object):
    def __init__(self, result):
        self._result = result

    @property
    def result(self):
        return self._result

class mongo(AbstractCmd):
    __option_parser__ = parser

    def _parse_args(self, cmdline):
        options, args = super()._parse_args(cmdline)
        if ":" in args[0]:
            options.host, options.database = args[0].split("/")
            options.host, options.port = options.host.split(":")
        elif "/" in args[0]:
            options.host, options.database = args[0].split("/")
        else:
            options.database = args[0]
        if len(args) > 1:
            args = args[1:]
        else:
            args = ""
        return options, args

    def connect(self):
        self.client = pymongo.MongoClient(host=self.options.host, port=self.options.port)
        self.db = self.client[self.options.database]
        self.db.authenticate(self.options.username, self.options.password, mechanism="SCRAM-SHA-1")
        master = self.db.command("ismaster")
        if not master["ismaster"]:
            self.client = pymongo.MongoClient(host=master["primary"])
            self.db = self.client[self.options.database]
            self.db.authenticate(self.options.username, self.options.password, mechanism="SCRAM-SHA-1")

    def close(self):
        with self.client:
            pass

    def run(self):
        return self.execute(self.args[0])

    def execute(self, command):
        result = eval(command, {"db": self.db})
        return Result(result)

    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.close()
