#!/usr/bin/env python
#
# See LICENSE file for copyright and license details.

"""Setup.py: build, distribute, clean."""

import os
import sys

from distutils import log
from distutils.core import setup
from glob import glob


setup(
    name='qt4reactor',
    version='1.0',
    license='MIT',
    author='Glenn H. Tarbox',
    author_email='glenn@tarbox.org',
    description='Twisted Qt4 Integration',
    long_description='Provides support for Twisted to be driven by the ' \
                     'Qt mainloop.',
    url='https://github.com/ghtdak/qtreactor',
    scripts=glob("./bin/*"),
    py_modules=['qt4reactor', 'gtrial'],
    data_files=['README', 'LICENSE'],
)
