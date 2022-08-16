# -*- coding: utf-8 -*-
from typing import Union, List
from abc import ABCMeta, abstractmethod
from optparse import OptionParser

from shtools.utils.cmdline import CmdLine


__all__ = ["AbstractCmd"]

class AbstractCmd(metaclass=ABCMeta):
    __option_parser__: OptionParser = None

    def __init__(self, cmdline: Union[str, List[str]]=""):
        self.options, self.args = self._parse_args(cmdline)

    def _parse_args(self, cmdline: Union[str, List[str]]):
        return self.__option_parser__.parse_args(self._get_args(cmdline))

    def _get_args(self, cmdline: Union[str, List[str]]):
        if isinstance(cmdline, str):
            return CmdLine.to_list(cmdline)
        return cmdline

    @classmethod
    def print_help(cls):
        cls.__option_parser__.print_help()

    @abstractmethod
    def run(self):
        pass
