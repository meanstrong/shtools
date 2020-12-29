# SHTools - some useful bash tools write in pure python.

## About
纯Python实现的一些bash命令工具集合.

## Requirements
- Python3

## Install
通过pip命令安装：
```shell
pip install shtools
```
或者通过下载源码包或clone代码至本地，然后通过如下命令安装：
```shell
python setup.py install
```

## Module
- curl: transfer a URL
- mongo: mongodb cli
- mysql: mysql cli
- nc: concatenate and redirect sockets
- ntpdate: set the date and time via NTP
- ping: send ICMP ECHO_REQUEST to network hosts
- psql: postgresql cli
- rediscli: redis cli
- scp: secure copy (remote file copy program)
- sh: shell
- ssh: OpenSSH SSH client (remote login program)

## Example
```python
from shtools.bash.mysql import Mysql
cmd = Mysql('-h 127.0.0.1 -P 3306 -u root -p ****** -D database -e "SELECT * FROM table"')
cmd.run()
```