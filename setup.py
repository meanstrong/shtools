#!/usr/bin/env python
# -*- coding:utf-8 -*-

from setuptools import setup, find_packages

with open("README.md", encoding="utf-8") as f:
    readme = f.read()

with open("LICENSE", encoding="utf-8") as f:
    license = f.read()

setup(
    name="shtools",
    version="1.0.9",
    packages=find_packages(exclude=["test*"]),
    # install_requires=["paramiko"],
    zip_safe=False,

    url="https://github.com/meanstrong/shtools",
    # license=license,
    description="some useful bash tools write in python",
    long_description=readme,
    long_description_content_type="text/markdown",
    author="pengmingqiang",
    author_email="rockypengchina@outlook.com",
    maintainer="pengmingqiang",
    maintainer_email="rockypengchina@outlook.com",
    platforms=['any'],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],

)
