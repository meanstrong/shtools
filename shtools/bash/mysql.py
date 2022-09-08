# -*- coding:utf-8 -*-
from optparse import OptionParser

import pymysql

from .abstract_cmd import AbstractCmd

__all__ = ["mysql"]

parser = OptionParser(usage="mysql [options...]", add_help_option=False)
parser.add_option("-D", "--database", action="store", dest="database", default="", help="Database to use.")
parser.add_option(
    "--default-character-set",
    action="store",
    dest="charset",
    default="utf8",
    help="Set the default character set.",
)
parser.add_option("-e", "--execute", action="store", dest="execute", default="", help="Execute command and quit.")
parser.add_option("-h", "--host", action="store", dest="host", default="localhost", help="Connect to host.")
parser.add_option(
    "-p",
    "--password",
    action="store",
    dest="password",
    default=None,
    help="Password to use when connecting to server.",
)
parser.add_option(
    "-P",
    "--port",
    action="store",
    type="int",
    dest="port",
    default=3306,
    help="Port number to use for connection or 0 for default to 3306.",
)
parser.add_option(
    "-u", "--user", action="store", dest="user", default="root", help="User for login if not current user."
)


class Result(object):
    def __init__(self, result):
        self._result = result

    @property
    def result(self):
        return self._result


class mysql(AbstractCmd):
    __option_parser__ = parser

    def connect(self):
        self.client = pymysql.connect(
            host=self.options.host,
            port=self.options.port,
            user=self.options.user,
            passwd=self.options.password,
            db=self.options.database,
            charset=self.options.charset,
        )

    def close(self):
        with self.client:
            pass

    def run(self):
        return self.execute(self.options.execute)
    
    def execute(self, command):
        self.client.execute(command)
        result = self.client.fetchall()
        return Result(result)

    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.close()
