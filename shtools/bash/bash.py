# -*- coding:utf-8 -*-
from subprocess import PIPE, Popen

from .abstract_cmd import AbstractCmd


__all__ = ["bash"]


class Result(object):
    def __init__(self, exit_code: int, stdout: bytes = b"", stderr: bytes = b""):
        self._exit_code = exit_code
        self._stdout = stdout
        self._stderr = stderr

    @property
    def exit_code(self):
        return self._exit_code

    @property
    def stdout(self):
        return self._stdout

    @property
    def stderr(self):
        return self._stderr


class bash(AbstractCmd):
    def _parse_args(self, cmdline):
        return None, [cmdline]

    def run(self):
        process = Popen(self.args[0], stdout=PIPE, stderr=PIPE, shell=True)
        stdout, stderr = process.communicate()
        exit_code = process.poll()
        return Result(exit_code=exit_code, stdout=stdout, stderr=stderr)
