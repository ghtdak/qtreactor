from __future__ import print_function
from __future__ import absolute_import

import sys

from ghtTests.texboxtest import buildgui

form = buildgui()

from twisted.internet import reactor
from twisted.python import log

log.startLogging(sys.stdout)

def shutdown():
    log.msg("got shutdown")


reactor.addSystemEventTrigger('before','shutdown',shutdown)

log.msg('calling reactor.run()')
reactor.run()
log.msg('fell off the bottom?...')

