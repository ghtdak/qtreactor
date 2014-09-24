from __future__ import print_function

__author__ = 'ght'

import sys

from twisted.application import reactors

reactors.installReactor('qt4')

from twisted.internet import reactor
from twisted.python import log

log.startLogging(sys.stdout)

resolve_helper = """
import sys
print sys.path
import {0}
{0}.install()
from twisted.internet import reactor

class Foo:
    def __init__(self):
        print sys.path
        reactor.callWhenRunning(self.start)
        self.timer = reactor.callLater(3, self.failed)
    def start(self):
        reactor.resolve('localhost').addBoth(self.done)
    def done(self, res):
        print 'done', res
        reactor.stop()
    def failed(self):
        print 'failed'
        self.timer = None
        reactor.stop()
f = Foo()
reactor.run()
""".format

import os

from twisted.internet import protocol, defer


class ChildResolveProtocol(protocol.ProcessProtocol):
    def __init__(self, onCompletion):
        self.onCompletion = onCompletion

    def connectionMade(self):
        self.output = []
        self.error = []

    def outReceived(self, out):
        self.output.append(out)

    def errReceived(self, err):
        self.error.append(err)

    def processEnded(self, reason):
        self.onCompletion.callback((reason, self.output, self.error))
        self.onCompletion = None

def spawn():

    helperPath = '/tmp/testspawn.py'
    helperFile = open(helperPath, 'w')

    # Eeueuuggg
    reactorName = reactor.__module__

    s=resolve_helper(reactorName)

    helperFile.write(s)
    helperFile.close()

    env = os.environ.copy()
    s=os.pathsep.join(['/Users/ght/PycharmProjects/qtreactor']+sys.path)
    log.msg("My Beautiful PATH",s," END OF MY BEAUTIFUL PATH")
    env['PYTHONPATH'] = s

    log.msg(env)

    helperDeferred = defer.Deferred()
    helperProto = ChildResolveProtocol(helperDeferred)

    reactor.spawnProcess(helperProto, sys.executable, ("python", "-u", helperPath), env)

    return helperDeferred

d = spawn()

def whathapp(result):
    log.msg("finished ", result)
    reactor.stop()

d.addCallback(whathapp)

reactor.run()
log.msg('fell off the bottom?...')
