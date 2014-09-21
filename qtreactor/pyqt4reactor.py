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

import qtreactor_config

qtreactor_config.set_qt_name("PyQt4")

import qt4base

if runtime.platform.getType() == 'win32':
    install = qt4base.win32install
else:
    install = qt4base.posixinstall

__all__ = ["install"]
