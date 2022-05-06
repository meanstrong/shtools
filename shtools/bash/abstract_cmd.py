# -*- coding: utf-8 -*-
from abc import ABCMeta, abstractmethod
from optparse import OptionParser

from shtools.utils.cmdline import CmdLine


__all__ = ["AbstractCmd"]

class AbstractCmd(metaclass=ABCMeta):
    __option_parser__: OptionParser = None

    def __init__(self, cmdline=""):
        self.options, self.args = self._cmdline_parse(cmdline)

    def _cmdline_parse(self, cmdline):
        return self.__option_parser__.parse_args(CmdLine.to_list(cmdline))

    @classmethod
    def print_help(cls):
        cls.__option_parser__.print_help()

    @abstractmethod
    def run(self):
        pass
