# -*- coding:utf-8 -*-
"""
公共log模块
v1.0.0:
    实现公共log模块
v1.0.1:
    判断logger属性是否已经有handler，若有则不再需要增加handler
"""

import os
import logging
import platform

__version__ = "1.0.1"
__author__ = "Rocky Peng"

if platform.system() == "Windows":
    from ctypes import windll, c_ulong

    def color_text_decorator(function):
        def real_func(self, string):
            windll.Kernel32.GetStdHandle.restype = c_ulong
            h = windll.Kernel32.GetStdHandle(c_ulong(0xFFFFFFF5))
            if function.__name__.upper() == "ERROR" or function.__name__.upper() == "EXCEPTION":
                windll.Kernel32.SetConsoleTextAttribute(h, 12)
            elif function.__name__.upper() == "WARN":
                windll.Kernel32.SetConsoleTextAttribute(h, 13)
            elif function.__name__.upper() == "INFO":
                windll.Kernel32.SetConsoleTextAttribute(h, 14)
            elif function.__name__.upper() == "DEBUG":
                windll.Kernel32.SetConsoleTextAttribute(h, 15)
            else:
                windll.Kernel32.SetConsoleTextAttribute(h, 15)
            function(self, string)
            windll.Kernel32.SetConsoleTextAttribute(h, 15)

        return real_func


else:

    def color_text_decorator(function):
        def real_func(self, string):
            if function.__name__.upper() == "ERROR" or function.__name__.upper() == "EXCEPTION":
                self.stream.write("\033[0;31;40m")
            elif function.__name__.upper() == "WARN":
                self.stream.write("\033[0;35;40m")
            elif function.__name__.upper() == "INFO":
                self.stream.write("\033[0;33;40m")
            elif function.__name__.upper() == "DEBUG":
                self.stream.write("\033[0;37;40m")
            else:
                self.stream.write("\033[0;37;40m")
            function(self, string)
            self.stream.write("\033[0m")

        return real_func


def singleton(cls, *args, **kw):
    instances = {}

    def _singleton(*args, **kw):
        if cls not in instances:
            instances[cls] = cls(*args, **kw)
        instances[cls].__init__(*args, **kw)
        return instances[cls]

    return _singleton


FORMAT = "[%(asctime)s] [%(name)s] [%(levelname)s] %(message)s"


class Logger(object):
    instances = {}

    def __new__(cls, name, *args, **kargs):
        if cls.instances.get(name) is not None:
            instance = cls.instances.get(name)
            instance.warn("Logger[%s] is already exists and will use that instance." % name)
        else:
            instance = super().__new__(cls)
            cls.instances[name] = instance
        return instance

    def __init__(self, name, level=logging.INFO, filename=None, filemode="w"):
        self.logger = logging.getLogger(name)
        if len(self.logger.handlers):
            # raise Exception("Duplicate logger names!!!")
            return
        self.logger.setLevel(logging.DEBUG)
        formatter = logging.Formatter(FORMAT)

        sh = logging.StreamHandler()
        sh.setFormatter(formatter)

        # sh.setLevel(logging.DEBUG)
        sh.setLevel(level)
        self.logger.addHandler(sh)
        self.stream = sh.stream

        if filename is not None:
            filepath = os.path.dirname(os.path.abspath(filename))
            if not os.path.exists(filepath):
                os.makedirs(filepath)
            fh = logging.FileHandler(filename, filemode)
            fh.setFormatter(formatter)
            fh.setLevel(logging.DEBUG)
            self.logger.addHandler(fh)

    @color_text_decorator
    def debug(self, string):
        return self.logger.debug(string)

    @color_text_decorator
    def info(self, string):
        return self.logger.info(string)

    @color_text_decorator
    def warn(self, string):
        return self.logger.warning(string)

    warnning = warn

    @color_text_decorator
    def error(self, string):
        return self.logger.error(string)

    @color_text_decorator
    def exception(self, string):
        return self.logger.exception(string)
