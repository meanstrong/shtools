# -*- coding: utf-8 -*-
from optparse import OptionParser
from typing import Any, List, Sequence, Union, Iterable
import json

from .abstract_cmd import AbstractCmd

__all__ = ["column"]

parser = OptionParser(usage="jq [options...] filter --input input")
parser.add_option("--indent", type="int", dest="indent", default=None, help="Use the given number of spaces (no more than 8) for indentation.")
parser.add_option("-S", "--sort-keys", action="store_true", dest="sort_keys", default=False, help="Output the fields of each object with the keys in sorted order.")
parser.add_option("--input", action="store", dest="input", default=None, help="input")


class jq(AbstractCmd):
    __option_parser__ = parser

    def input(self, input):
        """输入指定数据

        Args:
            input: 输入数据
        """
        self.options.input = input
        return self

    def run(self):
        if hasattr(self.options.input, "to_json"):
            return self.options.input.to_json()
        return json.dumps(self.options.input, indent=self.options.indent, sort_keys=self.options.sort_keys)

    def __str__(self) -> str:
        return self.run()
