# -*- coding: utf-8 -*-
# import select
import socket
import struct
import time
from optparse import OptionParser

from .bash import Bash


class Ntpdate(Bash):
    def get_parser(self):
        parser = OptionParser(usage="ntpdate [options...] <server>")
        parser.add_option(
            "-t",
            action="store",
            type="int",
            dest="timeout",
            default=1,
            help="Specify the maximum time waiting for a server response as the value timeout, in seconds and fraction. The value is is rounded to a multiple of 0.2 seconds. The default is 1 second, a value suitable for polling across a LAN.",
        )
        parser.add_option(
            "-u",
            action="store_true",
            dest="unprivileged",
            default=False,
            help="Direct  ntpdate to use an unprivileged port for outgoing packets. This is most useful when behind a firewall that blocks incoming traffic to privileged ports, and you want to synchronize with hosts beyond the firewall. Note that the -d option always uses unprivileged ports.",
        )
        return parser

    def run(self):
        ntp_server = self.args[0]
        ntp_port = 123
        # 创建一个ipv4 的 udp 连接
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.settimeout(self.options.timeout)
        """
        LI 3 未同步状态 2bit
        VN 3 ntp 版本3  3bit
        Mode 3 client 客户端模式 3bit
        Stratum 1 系统时钟层数取1 8bit
        Poll 10 两个报文相隔  8bit
        Precision 1 系统精度 8bit
        Root Delay 默认0 32bit 
        Root Dispersion 默认0 32bit
        Reference Identifier 默认0 32bit
        Reference Timestamp 默认0 64bit
        Originate Timestamp 默认0 64bit
        Receive Timestamp 默认0 64bit
        Transmit Timestamp 当前系统时间 64bit  0x83aa7e80 是1970 到 1900年的秒数
        Transmit Timestamp 高32位存秒数 低32位存毫秒 这里什么发0 也没可以用 ，程序自己记录下来就行
        """
        time1990_1970 = 0x83AA7E80

        # 包离开的时间
        t1 = time.time()
        # 使用struct pack 打包数据8bit 用 B 一个字节宽度 I 32bit  Q 64bit
        ntppack = struct.pack("!BBBBIIIQQQQ", 3 << 6 | 3 << 3 | 3, 1, 10, 1, 1, 10, 0, 0, 0, 0, 0)
        sock.sendto(ntppack, (ntp_server, ntp_port))
        try:
            resp, addr = sock.recvfrom(512)
        except socket.timeout:
            self.logger.exception("socket read timeout.")
            # return {"success": False, "msg": "no server suitable for synchronization found"}
            raise
        # 包到达的时间
        t4 = time.time()
        # 解包 这里LI VN Mode Stratum 等放到了一个64bit 的里面，所有格式和上面的打包不同
        (vi, root, refeTime, oriTime, receTime, tranTime) = struct.unpack("!QQQQQQ", resp)
        # Mode 是 4 是服务器返回标志
        if vi == vi | 4 << 56:
            # 64bit 1900年时间转普通时间
            receTime = receTime / (2 ** 32) - time1990_1970
            tranTime = tranTime / (2 ** 32) - time1990_1970
            t4 += ((receTime - t1) + (tranTime - t4)) / 2
            offset = time.time() - t4
        sock.close()
        # stdout = "adjust time server {} offset {:.6f} sec".format(self.args[0], offset)
        return dict(offset=offset)
