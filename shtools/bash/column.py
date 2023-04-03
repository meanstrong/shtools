# -*- coding: utf-8 -*-
from optparse import OptionParser
from typing import Any, Dict, Iterable, List, Sequence, Union

from .abstract_cmd import AbstractCmd

__all__ = ["column"]

parser = OptionParser(usage="column [options...] --input input")
parser.add_option("-t", "--table", action="store_true", dest="table", default=False, help="create a table")
parser.add_option("-s", "--separator", action="store", dest="separator", default=" ", help="possible table delimiters")
parser.add_option(
    "-o", "--output-separator", action="store", dest="output_separator", default="  ", help="table output column separator, default is two spaces"
)
parser.add_option("--input", action="store", dest="input", default=None, help="input")


class column(AbstractCmd):
    __option_parser__ = parser

    def input(self, input: Union[str, Iterable[Any]], orient: str = "sequence"):
        """输入指定数据

        Args:
            input (Union[str, Sequence[Any]]): 输入数据（可以是字符串或某种序列类型）
            orient (str, optional): 当输入数据类型是某种序列时，指定序列内元素的类型（sequence/dict/to-dict）. Defaults to "sequence".
        """
        self.options.input = input
        self._orient = orient
        return self

    def run(self):
        if not self.options.input:
            return ""
        if isinstance(self.options.input, str):
            if self.options.table:
                return self.by_sequence([[field for field in line.split(self.options.separator)] for line in self.options.input.splitlines()])
            return "\t".join(self.options.input.splitlines())
        if self._orient == "sequence":
            return self.by_sequence(self.options.input)
        if self._orient == "dict":
            return self.by_dict(self.options.input)
        if self._orient == "to-dict":
            return self.by_to_dict(self.options.input)
        return str(self.options.input)

    def by_to_dict(self, rows: Iterable):
        return self.by_dict(i.to_dict() for i in rows)

    def by_dict(self, dict_rows: Iterable[Dict]):
        keys = []
        rows = []
        for item in dict_rows:
            row = []
            for key in keys:
                row.append(item.get(key, ""))
            for key in (i for i in item.keys() if i not in keys):
                keys.append(key)
                row.append(item.get(key, ""))
            rows.append(row)
        rows.insert(0, keys)
        return self.by_sequence(rows)

    def by_sequence(self, rows: Iterable[Sequence]):
        rows = tuple(rows)
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

    def __str__(self) -> str:
        return self.run()
