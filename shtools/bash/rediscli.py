# -*- coding:utf-8 -*-
import time
from optparse import OptionParser

import redis
import rediscluster

from .abstract_cmd import AbstractCmd

__all__ = ["rediscli"]

parser = OptionParser(usage="rediscli [options...] [command]", add_help_option=False)
parser.add_option(
    "-h", action="store", dest="hostname", default="127.0.0.1", help="Server hostname (default: 127.0.0.1)."
)
parser.add_option("-p", action="store", type="int", dest="port", default=6379, help="Server port (default: 6379).")
parser.add_option(
    "-a", action="store", dest="password", default=None, help="Password to use when connecting to the server."
)
parser.add_option("-r", action="store", type="int", dest="repeat", default=1, help="Execute specified command N times.")
parser.add_option(
    "-i",
    action="store",
    type="int",
    dest="interval",
    default=1,
    help="When -r is used, waits <interval> seconds per command.\nIt is possible to specify sub-second times like -i 0.1.",
)
parser.add_option("-n", action="store", type="int", dest="db", default=0, help="Database number.")
parser.add_option(
    "-c",
    action="store_true",
    dest="cluster_mode",
    default=False,
    help="Enable cluster mode (follow -ASK and -MOVED redirections).",
)


class Result(object):
    def __init__(self, result):
        self._result = result

    @property
    def result(self):
        return self._result


class Rediscli(AbstractCmd):
    __option_parser__ = parser

    def run(self):
        result = None
        conn = redis.Redis(
            host=self.options.hostname,
            port=self.options.port,
            password=self.options.password,
            db=self.options.db,
            decode_responses=True,
        )
        if self.options.cluster_mode:
            out = conn.execute_command("cluster nodes")
            nodes = []
            for line in out.strip().split("\n"):
                host, port = line.split()[1].split(":")
                nodes.append({"host": host, "port": port})
            conn = rediscluster.StrictRedisCluster(
                startup_nodes=nodes, password=self.options.password, decode_responses=True
            )

        for _ in range(self.options.repeat):
            result = conn.execute_command(*self.args)
            time.sleep(self.options.interval)
        return Result(result)
