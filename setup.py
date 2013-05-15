#!/usr/bin/env python
#
# See LICENSE file for copyright and license details.

"""Setup.py: build, distribute, clean."""

from distutils.core import setup
from glob import glob

classifiers=[
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
    version='1.0',
    license='MIT',
    classifiers=classifiers,
    author='Glenn H. Tarbox',
    author_email='glenn@tarbox.org',
    description='Twisted Qt4 Integration',
    long_description='Provides support for Twisted to be driven by the '
                     'Qt mainloop.',
    url='https://github.com/ghtdak/qtreactor',
    scripts=glob("./bin/*"),
    py_modules=['qt4reactor', 'gtrial'],
)
