from __future__ import print_function

import sys

#from twisted.application import reactors

#reactors.installReactor('qt4')

from qt4reactor import install

install()


from twisted.internet import reactor, task
from twisted.python import log, runtime

log.startLogging(sys.stdout)

def testreactor():
    print('tick...')


def doit():
    log.msg("reactor module: ", reactor.__module__)
    task.LoopingCall(testreactor).start(1.0)
    reactor.callLater(5.0, reactor.stop)
    log.msg("platform runtime: " + repr(runtime.platform.getType()))


reactor.callWhenRunning(doit)
log.msg('calling reactor.run()')
reactor.run()
log.msg('fell off the bottom?...')
