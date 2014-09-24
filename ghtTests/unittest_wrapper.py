from __future__ import print_function
__author__ = 'ght'

import qtreactor.pyqt4reactor
#qtreactor.pyqt4reactor.install()

from twisted.application import reactors
reactors.installReactor('pyqt4')

#from ghtTests.texboxtest import buildgui

#form = buildgui()

import sys
#log.startLogging(sys.stdout)

trialpath = '/usr/local/bin/trial'
trial = open(trialpath,'r').read()

import contextlib
@contextlib.contextmanager
def redirect_argv(num):
    sys._argv = sys.argv[:]
    sys.argv[:] = num
    yield
    sys.argv[:] = sys._argv

def runTrial(*trials):
    with redirect_argv([trialpath]+list(trials)):
        exec (trial)

if __name__ == '__main__':
    runTrial(*['twisted.test.test_ftp',
              'twisted.test.test_internet'])
