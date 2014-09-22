# Copyright (c) 2001-2011 Twisted Matrix Laboratories.
# See LICENSE for details.
"""
See main docstring in module __init__.py

Reactor supporting PyQt4

API Stability: stable

Maintainer: U{Glenn H Tarbox, PhD<mailto:glenn@tarbox.org>}

"""

from __future__ import print_function, absolute_import

from twisted.python import runtime

from qtreactor import qtreactor_config

qtreactor_config.set_qt_name("PySide")

from qtreactor import qt4base

class pyqt4reactor(qt4base.QtReactor):
    pass

class pyqt4eventreactor(qt4base.QtReactor):
    pass

def posixinstall():
    """
    Install the Qt reactor.
    """
    p = pyqt4reactor()
    from twisted.internet.main import installReactor

    installReactor(p)


def win32install():
    """
    Install the Qt reactor.
    """
    p = pyqt4eventreactor()
    from twisted.internet.main import installReactor

    installReactor(p)

if runtime.platform.getType() == 'win32':
    install = win32install
else:
    install = posixinstall

__all__ = ["install"]
