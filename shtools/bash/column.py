# -*- coding: utf-8 -*-
from optparse import OptionParser
from typing import List, Sequence

import requests

from .abstract_cmd import AbstractCmd


__all__ = ["curl"]

parser = OptionParser(usage="column [options] [input]")
parser.add_option("-t", "--table", action="store_true", dest="table", default=False, help="create a table")
parser.add_option("-s", "--separator", action="store", dest="separator", default=None, help="possible table delimiters")
parser.add_option(
    "-o",
    "--output-separator",
    action="store",
    dest="output_separator",
    default="  ",
    help="table output column separator, default is two spaces",
)


class Result(object):
    def __init__(self, status_code: int, content: bytes):
        self._status_code = status_code
        self._content = content

    @property
    def status_code(self):
        return self._status_code

    @property
    def content(self):
        return self._content


class column(AbstractCmd):
    __option_parser__ = parser

    def run(self):
        if self.options.table:
            return self.to_string([[field for field in line.split(self.options.separator)] for line in self.args[0].splitlines()])
        return "\t".join(self.args[0].splitlines())

    def to_string(self, rows: Sequence[Sequence[str]]):
        max_column_count = max(len(row) for row in rows)
        max_field_len = [0] * max_column_count
        for row in rows:
            for i, field in enumerate(row):
                max_field_len[i] = max(max_field_len[i], len(field))
        lines: List[str] = []
        for row in rows:
            line: List[str] = []
            for i, field in enumerate(row):
                line.append(field + " " * (max_field_len[i] - len(field)))
            lines.append(self.options.output_separator.join(line))
        return "\n".join(lines)
