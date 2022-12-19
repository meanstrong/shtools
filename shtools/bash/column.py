# -*- coding: utf-8 -*-
from optparse import OptionParser
from typing import List, Sequence

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
    help="table output column separator, default is two spaces"
)


class column(AbstractCmd):
    __option_parser__ = parser

    def run(self):
        if self.options.table:
            return self.to_string([[field for field in line.split(self.options.separator)] for line in self.args[0].splitlines()])
        return "\t".join(self.args[0].splitlines())

    def to_string(self, rows: Sequence[Sequence]):
        max_column_count = max(len(row) for row in rows)
        max_field_len = [0] * max_column_count
        for row in rows:
            for i, field in enumerate(row):
                max_field_len[i] = max(max_field_len[i], len(str(field)))
        lines: List[str] = []
        for row in rows:
            line: List[str] = []
            for i, field in enumerate(row):
                line.append(str(field).ljust(max_field_len[i]))
            lines.append(self.options.output_separator.join(line))
        return "\n".join(lines)
