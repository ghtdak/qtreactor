__author__ = 'ght'


from twisted.application import reactors

reactors.installReactor('kqueue')

# Copyright (c) Twisted Matrix Laboratories.
# See LICENSE for details.

"""
Test running processes.
"""

import gzip
import os
import sys
import signal
import StringIO
import errno
import gc
import stat
import operator
try:
    import fcntl
except ImportError:
    fcntl = process = None
else:
    from twisted.internet import process


from zope.interface.verify import verifyObject

from twisted.python.log import msg
from twisted.internet import reactor, protocol, error, interfaces, defer
from twisted.trial import unittest
from twisted.python import util, runtime, procutils

from twisted.test import test_process

#testroot = "/usr/local/lib/python2.7/site-packages/twisted/test/process_fds.py"

testroot = __file__

class FDChecker(protocol.ProcessProtocol):
    state = 0
    data = ""
    failed = None

    def __init__(self, d):
        self.deferred = d

    def fail(self, why):
        self.failed = why
        self.deferred.callback(None)

    def connectionMade(self):
        self.transport.writeToChild(0, "abcd")
        self.state = 1

    def childDataReceived(self, childFD, data):
        if self.state == 1:
            if childFD != 1:
                self.fail("read '%s' on fd %d (not 1) during state 1" \
                          % (childFD, data))
                return
            self.data += data
            #print "len", len(self.data)
            if len(self.data) == 6:
                if self.data != "righto":
                    self.fail("got '%s' on fd1, expected 'righto'" \
                              % self.data)
                    return
                self.data = ""
                self.state = 2
                #print "state2", self.state
                self.transport.writeToChild(3, "efgh")
                return
        if self.state == 2:
            self.fail("read '%s' on fd %s during state 2" % (childFD, data))
            return
        if self.state == 3:
            if childFD != 1:
                self.fail("read '%s' on fd %s (not 1) during state 3" \
                          % (childFD, data))
                return
            self.data += data
            if len(self.data) == 6:
                if self.data != "closed":
                    self.fail("got '%s' on fd1, expected 'closed'" \
                              % self.data)
                    return
                self.state = 4
            return
        if self.state == 4:
            self.fail("read '%s' on fd %s during state 4" % (childFD, data))
            return

    def childConnectionLost(self, childFD):
        if self.state == 1:
            self.fail("got connectionLost(%d) during state 1" % childFD)
            return
        if self.state == 2:
            if childFD != 4:
                self.fail("got connectionLost(%d) (not 4) during state 2" \
                          % childFD)
                return
            self.state = 3
            self.transport.closeChildFD(5)
            return

    def processEnded(self, status):
        rc = status.value.exitCode
        if self.state != 4:
            self.fail("processEnded early, rc %d" % rc)
            return
        if status.value.signal != None:
            self.fail("processEnded with signal %s" % status.value.signal)
            return
        if rc != 0:
            self.fail("processEnded with rc %d" % rc)
            return
        self.deferred.callback(None)


class FDTest(unittest.TestCase):

    def testFD(self):
        exe = sys.executable
        scriptPath = util.sibpath(testroot, "process_fds.py")
        d = defer.Deferred()
        p = FDChecker(d)
        reactor.spawnProcess(p, exe, [exe, "-u", scriptPath], env=None,
                             path=None,
                             childFDs={0:"w", 1:"r", 2:2,
                                       3:"w", 4:"r", 5:"w"})
        def processEnded(ign):
            return self.failIf(p.failed, p.failed)
        d.addCallback(processEnded)
        return d

    def testLinger(self):
        # See what happens when all the pipes close before the process
        # actually stops. This test *requires* SIGCHLD catching to work,
        # as there is no other way to find out the process is done.
        exe = sys.executable
        scriptPath = util.sibpath(testroot, "process_linger.py")
        p = Accumulator()
        d = p.endedDeferred = defer.Deferred()
        reactor.spawnProcess(p, exe, [exe, "-u", scriptPath], env=None,
                             path=None,
                             childFDs={1:"r", 2:2},
                             )
        def processEnded(ign):
            self.assertEqual(p.outF.getvalue(),
                                 "here is some text\ngoodbye\n")
        return d.addCallback(processEnded)


class Accumulator(protocol.ProcessProtocol):
    """Accumulate data from a process."""

    closed = 0
    endedDeferred = None

    def connectionMade(self):
        self.outF = StringIO.StringIO()
        self.errF = StringIO.StringIO()

    def outReceived(self, d):
        self.outF.write(d)

    def errReceived(self, d):
        self.errF.write(d)

    def outConnectionLost(self):
        pass

    def errConnectionLost(self):
        pass

    def processEnded(self, reason):
        self.closed = 1
        if self.endedDeferred is not None:
            d, self.endedDeferred = self.endedDeferred, None
            d.callback(None)
