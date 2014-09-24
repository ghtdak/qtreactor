from __future__ import print_function

__author__ = 'ght'

# Copyright (c) Twisted Matrix Laboratories.
# See LICENSE for details.

# ---------------------------------
# Client

from twisted.application import reactors

reactors.installReactor('pyqt4')

from twisted.trial import unittest
from twisted.internet.protocol import DatagramProtocol
from twisted.internet import reactor, task


# noinspection PyClassHasNoInit
class EchoClientDatagramProtocol(DatagramProtocol):
    long_string = "-" * 1000

    def __init__(self):
        self.sendflag = True

    def stop_sending(self):
        self.sendflag = False

    def startProtocol(self):
        self.transport.connect('127.0.0.1', self.useport)
        self.senddatagram()

    def senddatagram(self):
        datagram = self.long_string
        self.transport.write(datagram)

    def datagramReceived(self, datagram, host):
        if self.sendflag:
            reactor.callLater(0.001, self.senddatagram)


def build_client(port, stopsend, stoplisten):
    protocol = EchoClientDatagramProtocol()
    protocol.useport = port
    r = reactor.listenUDP(0, protocol)
    reactor.callLater(stoplisten, r.stopListening)
    reactor.callLater(stopsend, protocol.stop_sending)
    return protocol

#------------------------------------------
# Server

# noinspection PyClassHasNoInit
class EchoUDP(DatagramProtocol):
    def datagramReceived(self, datagram, address):
        #log.msg("server received: ", repr(datagram), repr(address))
        self.transport.write(datagram, address)

def build_server(port, timeout):
    echo = EchoUDP()
    r = reactor.listenUDP(port, echo)
    reactor.callLater(timeout, r.stopListening)
    return echo

class TrialTest(unittest.TestCase):

    def setup(self):
        print("setup")

    def test_main(self):
        begin_port = 5010
        for port in xrange(begin_port, begin_port + 50):
            build_client(port, 10, 11)
            build_server(port, 12)

        def callme():
            print("deferLater callback")
            return 'he called'

        return task.deferLater(reactor, 15, callme)

    def tearDown(self):
        print('teardown')
