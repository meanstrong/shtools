# -*- coding: utf-8 -*-
# import select
import socket
import struct
import time
from optparse import OptionParser

from .abstract_cmd import AbstractCmd


__all__ = ["nc"]

parser = OptionParser(usage="nc [options...] [hostname] [port]")
parser.add_option(
    "-u", action="store_true", dest="udp", default=False, help="Use UDP instead of the default option of TCP."
)
parser.add_option("-v", action="store_true", dest="verbose", default=False, help="Have nc give more verbose output.")
parser.add_option(
    "-w",
    action="store",
    type="int",
    dest="timeout",
    default=5,
    help="If a connection and stdin are idle for more than timeout seconds, then the connection is silently closed.",
)
parser.add_option(
    "-z",
    action="store_true",
    dest="scan",
    default=False,
    help="Specifies that nc should just scan for listening daemons, without sending any data to them.",
)
parser.add_option("--stdin", action="store", type="string", dest="stdin", default=None, help="stdin message.")


class Result(object):
    def __init__(self, success: bool, reason: str = "", output: bytes = b""):
        self._success = success
        self._reason = reason
        self._output = output

    @property
    def success(self):
        return self._success

    @property
    def reason(self):
        return self._reason

    @property
    def output(self):
        return self._output


class nc(AbstractCmd):
    __option_parser__ = parser

    def run(self):
        with self.init_socket() as sock:
            if self.options.scan:
                if self.options.udp:
                    return self.scan_by_udp(sock)
                else:
                    return self.scan_by_tcp(sock)
            elif self.options.stdin:
                return self.communicate(sock)

    def init_socket(self):
        if self.options.udp:
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        else:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        return sock

    def scan_by_tcp(self, sock: socket.socket):
        # stdout = stderr = ""
        # exit_status = 0
        try:
            sock.connect((self.args[0], int(self.args[1])))
        except socket.error:
            return Result(success=False, reason="Connection refused")
        return Result(success=True)

    def scan_by_udp(self, sock: socket.socket):
        sock_icmp = None
        try:
            sock_icmp = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.getprotobyname("icmp"))
            sock_icmp.settimeout(5)
        except Exception as e:
            pass
        try:
            for _ in range(4):
                sock.sendto(b"X", (self.args[0], int(self.args[1])))
                time.sleep(1)
            if sock_icmp is not None:
                recPacket, addr = sock_icmp.recvfrom(64)
        except socket.timeout:
            return Result(success=True)
        if sock_icmp is not None:
            icmpHeader = recPacket[20:28]
            icmpPort = int(recPacket.encode("hex")[100:104], 16)
            head_type, code, checksum, packetID, sequence = struct.unpack("bbHHh", icmpHeader)
            sock_icmp.close()
            if code == 3 and icmpPort == int(self.args[1]) and addr[0] == self.args[0]:
                return Result(success=False, reason="Connection refused")
        return Result(success=True)

    def communicate(self, sock: socket.socket):
        try:
            sock.connect((self.args[0], int(self.args[1])))
            sock.settimeout(self.options.timeout)
        except socket.error:
            return Result(success=False, reason="Connection refused")
        try:
            sock.sendall(self.options.stdin.encode("utf-8"))
            receive = sock.recv(2048)
        except socket.error:
            return Result(success=False, reason="Failed to retrieve information from server")
        return Result(success=True, output=receive)
