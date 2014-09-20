# Copyright (c) 2001-2011 Twisted Matrix Laboratories.
# See LICENSE for details.
"""
See main docstring in module __init__.py

Reactor supporting PyQt4

API Stability: stable

Maintainer: U{Glenn H Tarbox, PhD<mailto:glenn@tarbox.org>}

"""

from __future__ import print_function

from twisted.python import runtime

import qt4reactor_config

qt4reactor_config.qt_type = "PySide"

import qtbase

if runtime.platform.getType() == 'win32':
    install = qtbase.win32install
else:
    install = qtbase.posixinstall

__all__ = ["install"]
