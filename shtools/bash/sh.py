# -*- coding:utf-8 -*-
import platform
# from optparse import OptionParser
from subprocess import PIPE, Popen

from .bash import Bash

if platform.system() == "Windows":
    coding = "gbk"
else:
    coding = "utf-8"


class Sh(Bash):
    def cmdlineparse(self, cmdline):
        return [cmdline]

    def parse_args(self, args):
        return None, args

    def run(self):
        self.logger.debug("shell: %s" % self.args[0])
        process = Popen(self.args[0], stdout=PIPE, stderr=PIPE, shell=True)
        stdout, stderr = process.communicate()
        stdout = stdout.decode(coding)
        stderr = stderr.decode(coding)
        rc = process.poll()
        # self.logger.debug("rc: %d" % rc)
        # self.logger.debug("stdout: %s" % stdout)
        # self.logger.warn("stderr: %s" % stderr)
        # if rc:
        #     raise CalledProcessError(rc, cmd, stdout)
        return dict(rc=rc, stdout=stdout, stderr=stderr)
