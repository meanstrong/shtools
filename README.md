# SHTools - some useful bash tools write in pure python.

![image](https://img.shields.io/badge/made_in-china-ff2121.svg)
[![image](https://img.shields.io/pypi/v/shtools.svg)](https://pypi.org/project/shtools/)
[![image](https://img.shields.io/pypi/l/shtools.svg)](https://pypi.org/project/shtools/)

## About
纯Python实现的一些CLI命令工具集合.

## Requirements
- Python3

## Install
通过pip命令安装：
```shell
pip install shtools[ssh]
```
或者通过下载源码包或clone代码至本地，然后通过如下命令安装：
```shell
python setup.py install
```

## cli command
- curl: transfer a URL
- mongo: mongodb cli
- mysql: mysql cli
- nc: concatenate and redirect sockets
- ntpdate: set the date and time via NTP
- ping: send ICMP ECHO_REQUEST to network hosts
- psql: postgresql cli
- rediscli: redis cli
- scp: secure copy (remote file copy program)
- bash: local shell command
- ssh: OpenSSH SSH client (remote login program)

## Example
```python
from shtools.bash.mysql import mysql

# print help
mysql.print_help()

# run
cmd = mysql('-h 127.0.0.1 -P 3306 -u root -p ****** -D database -e "SELECT * FROM table"')
result = cmd.run()
```
