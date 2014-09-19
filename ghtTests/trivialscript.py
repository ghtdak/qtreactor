from __future__ import print_function

import sys

from twisted.application import reactors

reactors.installReactor('pyside')

from twisted.internet import reactor, task
from twisted.python import log, runtime

log.startLogging(sys.stdout)


def testreactor():
    print('tick...')


def doit():
    task.LoopingCall(testreactor).start(10.0)
    reactor.callLater(1500.0, reactor.stop)
    log.msg("platform runtime: " + repr(runtime.platform.getType()))


reactor.callWhenRunning(doit)
log.msg('calling reactor.run()')
reactor.run()
log.msg('fell off the bottom?...')

# sys.exit(app.exec_())

