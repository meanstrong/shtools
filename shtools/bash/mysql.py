# -*- coding:utf-8 -*-
from optparse import OptionParser

import pymysql

from .bash import Bash


class Mysql(Bash):
    def get_parser(self):
        parser = OptionParser(usage="mysql [options...]", add_help_option=False)
        parser.add_option("-D", "--database", action="store", dest="database", default="", help="Database to use.")
        parser.add_option(
            "--default-character-set",
            action="store",
            dest="charset",
            default="utf8",
            help="Set the default character set.",
        )
        parser.add_option(
            "-e", "--execute", action="store", dest="execute", default="", help="Execute command and quit."
        )
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
        return parser

    def run(self):
        result = None
        with pymysql.connect(
            host=self.options.host,
            port=self.options.port,
            user=self.options.user,
            passwd=self.options.password,
            db=self.options.database,
            charset=self.options.charset,
        ) as cur:
            cur.execute(self.options.execute)
            result = cur.fetchall()
        return result
