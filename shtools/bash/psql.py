# -*- coding:utf-8 -*-
from optparse import OptionParser

import psycopg2

from .abstract_cmd import AbstractCmd

__all__ = ["psql"]

parser = OptionParser(usage="psql [options...]", add_help_option=False)
parser.add_option(
    "-c",
    "--command",
    action="store",
    dest="command",
    default="",
    help="run only single command (SQL or internal) and exit",
)
parser.add_option(
    "-d",
    "--dbname",
    action="store",
    dest="dbname",
    default="root",
    help='database name to connect to (default: "root")',
)
parser.add_option(
    "-l", "--list", action="store_true", dest="list", default=False, help="list available databases, then exit"
)
parser.add_option(
    "-h",
    "--host",
    action="store",
    dest="host",
    default="localhost",
    help='database server host or socket directory (default: "local socket")',
)
parser.add_option(
    "-p", "--port", action="store", type="int", dest="port", default=5432, help='database server port (default: "5432")'
)
parser.add_option(
    "-U", "--username", action="store", dest="username", default="root", help="User for login if not current user."
)
parser.add_option(
    "-W", "--password", action="store", dest="password", default=None, help="Password to use when connecting to server."
)


class Result(object):
    def __init__(self, result):
        self._result = result

    @property
    def result(self):
        return self._result


class psql(AbstractCmd):
    __option_parser__ = parser

    def connect(self):
        self.conn = psycopg2.connect(
            host=self.options.host,
            port=self.options.port,
            user=self.options.username,
            password=self.options.password,
            database=self.options.dbname,
        )
        self.cur = self.conn.cursor()

    def execute(self, command):
        self.cur.execute(command)
        self.conn.commit()
        result = self.cur.fetchall()
        return Result(result)

    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.cur.close()
        self.conn.close()
