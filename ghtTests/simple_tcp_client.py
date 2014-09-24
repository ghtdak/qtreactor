from __future__ import print_function
__author__ = 'ght'

# Copyright (c) Twisted Matrix Laboratories.
# See LICENSE for details.

from twisted.application import reactors

reactors.installReactor('qt4')

from twisted.python import log
import sys
log.startLogging(sys.stdout)

"""
An example client. Run simpleserv.py first before running this.
"""

from twisted.internet import reactor, protocol

import q

# a client protocol

class EchoClient(protocol.Protocol):
    """Once connected, send a message, then print the result."""

    def connectionMade(self):
        q('client')
        self.transport.write("hello, world!")

    def dataReceived(self, data):
        q('client received: ', data)
        "As soon as any data is received, write it back."
        log.msg("Server said:", data)
        reactor.callLater(1.0, self.writeAgain)
        #self.transport.loseConnection()

    def writeAgain(self):
        q('client doing it again')
        self.transport.write("Helloooo again!!!!")

    def connectionLost(self, reason):
        q('client')
        log.msg("connection lost")

class EchoFactory(protocol.ClientFactory):
    protocol = EchoClient

    def clientConnectionFailed(self, connector, reason):
        q('client',connector,reason)
        log.msg("Connection failed - goodbye!")
        #reactor.stop()

    def clientConnectionLost(self, connector, reason):
        q('client',connector,reason)
        log.msg("Connection lost - goodbye!")
        #reactor.stop()


# this connects the protocol to a server runing on port 8000
def main():
    f = EchoFactory()
    reactor.connectTCP("127.0.0.1", 8000, f)
    reactor.run()

# this only runs if the module was *not* imported
if __name__ == '__main__':
    main()