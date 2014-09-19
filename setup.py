#!/usr/bin/env python
#
# See LICENSE file for copyright and license details.

"""Setup.py: build, distribute, clean."""

from distutils.core import setup
from glob import glob

classifiers = [
    'Development Status :: 5 - Production/Stable',
    'Environment :: X11 Applications :: Qt',
    'Framework :: Twisted',
    'Intended Audience :: Developers',
    'License :: OSI Approved :: MIT License',
    'Operating System :: OS Independent',
    'Programming Language :: Python',
]

setup(
    name='qt4reactor',
    version='1.5',
    license='MIT',
    classifiers=classifiers,
    author='Glenn H. Tarbox',
    author_email='glenn@tarbox.org',
    description='Twisted Qt Integration',
    long_description='Twisted Qt Event Loop integration for Pyqt4 and PySide',
    url='https://github.com/ghtdak/qtreactor',
    scripts=glob("./bin/*"),
    py_modules=['qt4reactor', 'gtrial', 'pysidereactor', 'qtbase'],
    requires=['twisted'],
    extras_require={
        'PyQt4', ['PyQt4'],
        'PySide', ['PySide']
    }
)
