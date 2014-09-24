from __future__ import print_function
from __future__ import absolute_import

import sys

from testmodule.texboxtest import buildgui

form = buildgui()

from twisted.internet import reactor, task
from twisted.python import log, runtime

log.startLogging(sys.stdout)

from qtreactor.pyqt4reactor import pyqt4reactor

def testreactor():
    print('tick...')
    form.edit2.setText(str(pyqt4reactor.pingcount))


def doit():
    task.LoopingCall(testreactor).start(1.0)
    reactor.callLater(5.0, reactor.stop)
    log.msg("platform runtime: " + repr(runtime.platform.getType()))


reactor.callWhenRunning(doit)
log.msg('calling reactor.run()')
reactor.run()
log.msg('fell off the bottom?...')
