#!/usr/bin/env python
# -*- coding:utf-8 -*-

from setuptools import setup, find_packages

import shtools


with open("README.md", encoding="utf-8") as f:
    readme = f.read()

setup(
    name="shtools",
    version=shtools.__version__,
    packages=find_packages(exclude=["test*"]),
    zip_safe=False,

    url="https://github.com/meanstrong/shtools",
    description="some useful bash tools write in python",
    long_description=readme,
    long_description_content_type="text/markdown",
    author="pengmingqiang",
    author_email="rockypengchina@outlook.com",
    maintainer="pengmingqiang",
    maintainer_email="rockypengchina@outlook.com",
    platforms=['any'],
    license="GPLv3",
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],

)
