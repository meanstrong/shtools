#!/usr/bin/env python

"""
    A pure python ping implementation using raw socket.
  
  
    Note that ICMP messages can only be sent from processes running as root.
  
  
    Derived from ping.c distributed in Linux's netkit. That code is
    copyright (c) 1989 by The Regents of the University of California.
    That code is in turn derived from code written by Mike Muuss of the
    US Army Ballistic Research Laboratory in December, 1983 and
    placed in the public domain. They have my thanks.
  
    Bugs are naturally mine. I'd be glad to hear about them. There are
    certainly word - size dependenceies here.
  
    Copyright (c) Matthew Dixon Cowles, <http://www.visi.com/~mdc/>.
    Distributable under the terms of the GNU General Public License
    version 2. Provided with no warranties of any sort.
  
    Original Version from Matthew Dixon Cowles:
      -> ftp://ftp.visi.com/users/mdc/ping.py
  
    Rewrite by Jens Diemer:
      -> http://www.python-forum.de/post-69122.html#69122
  
    Rewrite by George Notaras:
      -> http://www.g-loaded.eu/2009/10/30/python-ping/
 
    Fork by Pierre Bourdon:
      -> http://bitbucket.org/delroth/python-ping/
  
    Revision history
    ~~~~~~~~~~~~~~~~
  
    November 22, 1997
    -----------------
    Initial hack. Doesn't do much, but rather than try to guess
    what features I (or others) will want in the future, I've only
    put in what I need now.
  
    December 16, 1997
    -----------------
    For some reason, the checksum bytes are in the wrong order when
    this is run under Solaris 2.X for SPARC but it works right under
    Linux x86. Since I don't know just what's wrong, I'll swap the
    bytes always and then do an htons().
  
    December 4, 2000
    ----------------
    Changed the struct.pack() calls to pack the checksum and ID as
    unsigned. My thanks to Jerome Poincheval for the fix.
  
    May 30, 2007
    ------------
    little rewrite by Jens Diemer:
     -  change socket asterisk import to a normal import
     -  replace time.time() with time.clock()
     -  delete "return None" (or change to "return" only)
     -  in checksum() rename "str" to "source_string"
  
    November 8, 2009
    ----------------
    Improved compatibility with GNU/Linux systems.
  
    Fixes by:
     * George Notaras -- http://www.g-loaded.eu
    Reported by:
     * Chris Hallman -- http://cdhallman.blogspot.com
  
    Changes in this release:
     - Re-use time.time() instead of time.clock(). The 2007 implementation
       worked only under Microsoft Windows. Failed on GNU/Linux.
       time.clock() behaves differently under the two OSes[1].
  
    [1] http://docs.python.org/library/time.html#time.clock
"""

__version__ = "0.1"
__all__ = ["ping"]


import os
import select
import socket
import struct
import time
from optparse import OptionParser

from .abstract_cmd import AbstractCmd

# logging.basicConfig(level=logging.DEBUG,
#                 format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
# logger = logging.getLogger('Ping')
#
# From /usr/include/linux/icmp.h; your milage may vary.
ICMP_ECHO_REQUEST = 8  # Seems to be the same on Solaris.
SEQUENCE_NUMBER = 0


def checksum(source_string):
    """
    I'm not too confident that this is right but testing seems
    to suggest that it gives the same answers as in_cksum in ping.c
    """
    sum = 0
    countTo = (len(source_string) / 2) * 2
    count = 0
    while count < countTo:
        # thisVal = ord(source_string[count + 1])*256 + ord(source_string[count])
        thisVal = (source_string[count + 1]) * 256 + source_string[count]
        sum = sum + thisVal
        sum = sum & 0xFFFFFFFF  # Necessary?
        count = count + 2

    if countTo < len(source_string):
        # sum = sum + ord(source_string[len(source_string) - 1])
        sum = sum + source_string[len(source_string) - 1]
        sum = sum & 0xFFFFFFFF  # Necessary?

    sum = (sum >> 16) + (sum & 0xFFFF)
    sum = sum + (sum >> 16)
    answer = ~sum
    answer = answer & 0xFFFF

    # Swap bytes. Bugger me if I know why.
    answer = answer >> 8 | (answer << 8 & 0xFF00)

    return answer


def receive_one_ping(my_socket, ID, timeout):
    """
    receive the ping from the socket.
    """
    timeLeft = timeout
    while True:
        startedSelect = time.time()
        whatReady = select.select([my_socket], [], [], timeLeft)
        howLongInSelect = time.time() - startedSelect
        if whatReady[0] == []:  # Timeout
            return

        timeReceived = time.time()
        recPacket, addr = my_socket.recvfrom(1024)
        icmpHeader = recPacket[20:28]
        type, code, checksum, packetID, sequence = struct.unpack("bbHHh", icmpHeader)
        if packetID == ID:
            bytesInDouble = struct.calcsize("d")
            timeSent = struct.unpack("d", recPacket[28:28 + bytesInDouble])[0]
            return timeReceived - timeSent

        timeLeft = timeLeft - howLongInSelect
        if timeLeft <= 0:
            return


def send_one_ping(my_socket, dest_addr, ID):
    """
    Send one ping to the given >dest_addr<.
    """
    global SEQUENCE_NUMBER
    dest_addr = socket.gethostbyname(dest_addr)

    # Header is type (8), code (8), checksum (16), id (16), sequence (16)
    my_checksum = 0

    # sequence number
    SEQUENCE_NUMBER = (SEQUENCE_NUMBER + 1) % 32768

    # Make a dummy heder with a 0 checksum.
    header = struct.pack("bbHHh", ICMP_ECHO_REQUEST, 0, my_checksum, ID, SEQUENCE_NUMBER)
    bytesInDouble = struct.calcsize("d")
    # data = (192 - bytesInDouble) * "Q"
    data = struct.pack("d", time.time()) + str.encode((192 - bytesInDouble) * "Q")

    # Calculate the checksum on the data and the dummy header.
    my_checksum = checksum(header + data)

    # Now that we have the right checksum, we put that in. It's just easier
    # to make up a new header than to stuff it into the dummy.
    header = struct.pack("bbHHh", ICMP_ECHO_REQUEST, 0, socket.htons(my_checksum), ID, SEQUENCE_NUMBER)
    packet = header + data
    my_socket.sendto(packet, (dest_addr, 1))  # Don't know about the 1


def do_one(dest_addr, timeout):
    """
    Returns either the delay (in seconds) or none on timeout.
    """
    icmp = socket.getprotobyname("icmp")
    try:
        my_socket = socket.socket(socket.AF_INET, socket.SOCK_RAW, icmp)
    except socket.error as e:
        if e.errno == 1:
            # Operation not permitted
            msg = str(e) + (" - Note that ICMP messages can only be sent from processes" " running as root.")
            raise socket.error(msg)
        raise  # raise the original error

    my_ID = os.getpid() & 0xFFFF

    send_one_ping(my_socket, dest_addr, my_ID)
    delay = receive_one_ping(my_socket, my_ID, timeout)

    my_socket.close()
    return delay


def verbose_ping(dest_addr, timeout=2, count=4):
    """
    Send >count< ping to >dest_addr< with the given >timeout< and display
    the result.
    """
    for i in range(count):
        print("ping %s..." % dest_addr)
        try:
            delay = do_one(dest_addr, timeout)
        except socket.gaierror as e:
            print("failed. (socket error: '%s')" % e[1])
            break

        if delay is None:
            print("failed. (timeout within %ssec.)" % timeout)
        else:
            delay = delay * 1000
            print("get ping in %0.4fms" % delay)
    print()


def check_ping(dest_addr, timeout=2, count=4):
    """
    Send >count< ping to >dest_addr< with the given >timeout< and return True or False.
    """
    response_num = ping(dest_addr, timeout, count)
    if response_num == count:
        return True
    else:
        return False


def ping(dest_addr, timeout=2, count=4):
    """
    Send >count< ping to >dest_addr< with the given >timeout< and return response package number.
    """
    response_num = 0
    for i in range(count):
        try:
            delay = do_one(dest_addr, timeout)
        except socket.gaierror as e:
            print("ping %s...failed. (socket error: '%s')" % (dest_addr, str(e)))
            continue
            # break
        except socket.error as e:
            print("ping %s...failed. (socket error: '%s')" % (dest_addr, str(e)))
            continue

        if delay is None:
            print("ping %s...failed. (timeout within %ssec.)" % (dest_addr, timeout))
        else:
            delay = delay * 1000
            print("ping %s...OK. (get ping in %0.4fms.)" % (dest_addr, delay))
            response_num += 1

    loss = count - response_num
    loss_rate = 100 * loss / count
    print("Packets: Sent = %s, Received = %s, Lost = %s (%s%% loss)" % (count, response_num, loss, loss_rate))

    return response_num


parser = OptionParser(usage="ping [options...] <destination>")
parser.add_option(
    "-c", action="store", type="int", dest="count", default=5, help="Stop after sending count ECHO_REQUEST packets."
)
parser.add_option("-v", action="store_true", dest="verbose", default=False, help="Verbose output.")
parser.add_option(
    "-W", action="store", type="int", dest="timeout", default=5, help="Time to wait for a response, in seconds."
)


class Result(object):
    def __init__(self, sent: int, received: int, packet_loss: float):
        self._sent = sent
        self._received = received
        self._packet_loss = packet_loss

    @property
    def sent(self):
        return self._sent

    @property
    def received(self):
        return self._received

    @property
    def packet_loss(self):
        return self._packet_loss

    def __str__(self):
        return f"{self._sent} packets transmitted, {self._received} received, {self._packet_loss}% packet loss"


class ping(AbstractCmd):
    __option_parser__ = parser

    def run(self):
        dest_addr = self.args[0]
        timeout = self.options.timeout
        sent = self.options.count

        received = 0
        for i in range(sent):
            try:
                delay = do_one(dest_addr, timeout)
            except socket.gaierror as e:
                continue
            except socket.error as e:
                continue

            if delay is not None:
                delay = delay * 1000
                received += 1

        loss = sent - received
        packet_loss = 100 * loss / sent

        return Result(sent=sent, received=received, packet_loss=packet_loss)


if __name__ == "__main__":
    verbose_ping("heise.de")
    verbose_ping("google.com")
    verbose_ping("a-test-url-taht-is-not-available.com")
    verbose_ping("192.168.1.1")
