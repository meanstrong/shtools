# -*- coding: utf-8 -*-
from abc import ABCMeta, abstractmethod
from optparse import OptionParser

from shtools.utils.cmdline import CmdLine
from shtools.utils.log import Logger

logger = Logger("SHTools")


class Bash(metaclass=ABCMeta):
    def __init__(self, cmdline=""):
        self.logger = logger
        self.parser = self.get_parser()
        self.options, self.args = self.parse_args(self.cmdlineparse(cmdline))

    def cmdlineparse(self, cmdline):
        return CmdLine.to_list(cmdline)

    def print_help(self):
        self.parser.print_help()

    def get_parser(self):
        return OptionParser()

    def parse_args(self, args):
        return self.parser.parse_args(args)

    # @abstractmethod
    # def optparse(self, args):
    #     pass

    @abstractmethod
    def run(self):
        pass
