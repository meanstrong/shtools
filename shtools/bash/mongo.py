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

    def _cmdline_parse(self, cmdline):
        options, args = super()._cmdline_parse(cmdline)
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

    def run(self):
        conn = pymongo.MongoClient(host=self.options.host, port=self.options.port)
        db = conn[self.options.database]
        db.authenticate(self.options.username, self.options.password, mechanism="SCRAM-SHA-1")
        master = db.command("ismaster")
        if not master["ismaster"]:
            conn = pymongo.MongoClient(host=master["primary"])
            db = conn[self.options.database]
            db.authenticate(self.options.username, self.options.password, mechanism="SCRAM-SHA-1")
        result = eval(self.args[0])
        conn.close()
        return Result(result)
