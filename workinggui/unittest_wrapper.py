from __future__ import print_function
__author__ = 'ght'

from twisted.application import reactors

reactors.installReactor('pyqt4')

from twisted.internet.task import  LoopingCall
from twisted.internet import  reactor

from twisted.python import log

import sys
#log.startLogging(sys.stdout)

trialpath = '/usr/local/bin/trial'
trial = open(trialpath,'r').read()

def aliveness():
    print('tick')

lc = LoopingCall(aliveness)

def shutdown():
    lc.stop()

lc = LoopingCall(aliveness)
reactor.addSystemEventTrigger('before','shutdown',shutdown)
lc.start(1)

import contextlib
@contextlib.contextmanager
def redirect_argv(num):
    sys._argv = sys.argv[:]
    sys.argv[:] = num
    yield
    sys.argv[:] = sys._argv

print(sys.argv)

with redirect_argv([trialpath,
                    'twisted.test.test_ftp']):
    exec (trial)
