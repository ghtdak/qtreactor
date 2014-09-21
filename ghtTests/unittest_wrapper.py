from __future__ import print_function
__author__ = 'ght'


from twisted.application import reactors

reactors.installReactor('pyqt4')

from runpy import run_module

#run_module('twisted.trial.unittest', 'twisted.test.test_ftp')

trialpath = '/usr/local/bin/trial'
trial = open(trialpath,'r').read()

import sys
import contextlib
@contextlib.contextmanager
def redirect_argv(num):
    sys._argv = sys.argv[:]
    sys.argv[:] = num
    yield
    sys.argv[:] = sys._argv

print(sys.argv)

with redirect_argv([trialpath,
                    'twisted.test.test_internet']):
    print(sys.argv)

    exec (trial)
