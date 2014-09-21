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

# restricts pyside loading if config is pre-set.

if qtreactor_config.qt_type == "":

    qtreactor_config.qt_type = "PySide"

    import qt4base

    if runtime.platform.getType() == 'win32':
        install = qt4base.win32install
    else:
        install = qt4base.posixinstall

    __all__ = ["install"]
