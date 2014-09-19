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

import __init__ as superinit

superinit.setqtname('PyQt4')

import qtbase


if runtime.platform.getType() == 'win32':
    # noinspection PyUnresolvedReferences
    from win32event import (WAIT_OBJECT_0, WAIT_TIMEOUT,
                            QS_ALLINPUT, QS_ALLEVENTS)

    install = qtbase.win32install
else:
    install = qtbase.posixinstall

__all__ = ["install"]
