# -*- coding: utf-8 -*-
# import select
import socket
import struct
import time
from optparse import OptionParser

from .bash import Bash


class Nc(Bash):
    def get_parser(self):
        parser = OptionParser(usage="ncat [options...] [hostname] [port]")
        parser.add_option(
            "-u", action="store_true", dest="udp", default=False, help="Use UDP instead of the default option of TCP."
        )
        parser.add_option(
            "-v", action="store_true", dest="verbose", default=False, help="Have nc give more verbose output."
        )
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
        return parser

    def run(self):
        sock = self.init_socket()
        if self.options.scan:
            if self.options.udp:
                result = self.scan_by_udp(sock)
            else:
                result = self.scan_by_tcp(sock)
            sock.close()
            return result

        if self.options.stdin:
            result = self.communicate(sock)
            sock.close()
            return result
        raise Exception("unkown command")

    def init_socket(self):
        if self.options.udp:
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.logger.debug("socket UDP.")
        else:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.logger.debug("socket TCP.")
        return sock

    def scan_by_tcp(self, sock):
        # stdout = stderr = ""
        # exit_status = 0
        try:
            sock.connect((self.args[0], int(self.args[1])))
            self.logger.info("connect to {} OK.".format(self.args))
        except socket.error:
            # stderr = "connect to {} port {} (tcp) failed: Connection refused".format(self.args[0], self.args[1])
            raise
        # else:
        #     stdout = "Connection to {} {} port [tcp/*] succeeded!".format(self.args[0], self.args[1])
        return dict(success=True)

    def scan_by_udp(self, sock):
        # stdout = stderr = ""
        sock_icmp = None
        try:
            sock_icmp = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.getprotobyname("icmp"))
            sock_icmp.settimeout(5)
        except Exception as e:
            self.logger.warn("icmp socket error: {}.".format(e))
        try:
            for i in range(4):
                sock.sendto(b"X", (self.args[0], int(self.args[1])))
                time.sleep(1)
            if sock_icmp is not None:
                recPacket, addr = sock_icmp.recvfrom(64)
                self.logger.info("receive package: {}.".format(recPacket))
        except socket.timeout:
            # stdout = "Connection to {} {} port [udp/*] succeeded!".format(self.args[0], self.args[1])
            return dict(success=True)
        # except Exception:
        #     return "", "", 1
        if sock_icmp is not None:
            icmpHeader = recPacket[20:28]
            icmpPort = int(recPacket.encode("hex")[100:104], 16)
            head_type, code, checksum, packetID, sequence = struct.unpack("bbHHh", icmpHeader)
            sock_icmp.close()
            if code == 3 and icmpPort == int(self.args[1]) and addr[0] == self.args[0]:
                # stderr = "connect to {} port {} (udp) failed: Connection refused".format(self.args[0], self.args[1])
                raise Exception("Connection refused")
        # stdout = "Connection to {} {} port [udp/*] succeeded!".format(self.args[0], self.args[1])
        return dict(success=True)

    def communicate(self, sock):
        try:
            sock.connect((self.args[0], int(self.args[1])))
            sock.settimeout(self.options.timeout)
            self.logger.info("connect to {} OK.".format(self.args))
        except socket.error:
            # stderr = "connect to {} port {} ({}) failed: Connection refused".format(
            #     self.args[0], self.args[1], self.options.udp and "udp" or "tcp"
            # )
            raise
        # sock.setblocking(0)
        # ready = select.select([sock], [], [], self.options.timeout)
        try:
            sock.sendall(self.options.stdin.encode("utf-8"))
            # log("communicate ready: {}.".format(ready))
            # if ready[0]:
            receive = sock.recv(2048).decode("utf-8")
            self.logger.info("communicate receive: {}.".format(receive))
        except socket.error:
            # return {"success": False, "msg": "Failed to retrieve information from server"}
            raise
        return dict(success=True, receive=receive)
