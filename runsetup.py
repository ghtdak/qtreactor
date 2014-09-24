#!/usr/local/bin/python

__author__ = 'ght'
"""
This file isn't part of the distribution.  Its for cleaning up before making the
distribution with setuptools.
"""

import os, shutil, tempfile

f = tempfile.mkdtemp(dir='/tmp')

shutil.move('.idea', f+'/tempidea')

os.system('/usr/bin/git clean -dfx')

shutil.move(f+'/tempidea'', '.idea')

os.system('/usr/local/bin/python setup.py sdist')

