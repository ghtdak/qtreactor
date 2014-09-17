# Copyright (c) 2001-2011 Twisted Matrix Laboratories.
# See LICENSE for details.
"""

Reactor for PySide

API Stability: stable

Maintainer: U{Glenn H Tarbox, PhD<mailto:glenn@tarbox.org>}

"""

from __future__ import print_function
import sys

from zope.interface import implements
from twisted.internet.interfaces import IReactorFDSet
from twisted.python import log, runtime
from twisted.internet import posixbase


# noinspection PyUnresolvedReferences
import PySide.QtScript as QtScript
# noinspection PyUnresolvedReferences
import PySide.QtGui as QtGui
# noinspection PyUnresolvedReferences
import PySide.QtCore as QtCore


# noinspection PyBroadException
class TwistedSocketNotifier(QtCore.QObject):
    """
    Connection between an fd event and reader/writer callbacks.
    """

    def __init__(self, parent, reactor, watcher, socket_type):
        QtCore.QObject.__init__(self, parent)
        self.reactor = reactor
        self.watcher = watcher
        fd = watcher.fileno()
        self.notifier = QtCore.QSocketNotifier(fd, socket_type, parent)
        self.notifier.setEnabled(True)
        if socket_type == QtCore.QSocketNotifier.Read:
            self.fn = self.read
        else:
            self.fn = self.write
        QtCore.QObject.connect(self.notifier, QtCore.SIGNAL("activated(int)"), self.fn)

    def shutdown(self):
        self.notifier.setEnabled(False)
        self.disconnect(self.notifier, QtCore.SIGNAL("activated(int)"), self.fn)
        self.fn = self.watcher = None
        self.notifier.deleteLater()
        self.deleteLater()

    # noinspection PyUnusedLocal
    def read(self, fd):
        if not self.watcher:
            return
        w = self.watcher
        # doRead can cause self.shutdown to be called so keep a
        # reference to self.watcher

        # noinspection PyProtectedMember
        def _read():
            # Don't call me again, until the data has been read
            self.notifier.setEnabled(False)
            try:
                data = w.doRead()
            except:
                log.err()
                self.reactor._disconnectSelectable(w, sys.exc_info()[1], False)
            else:
                if data:
                    self.reactor._disconnectSelectable(w, data, True)
                elif self.watcher:
                    self.notifier.setEnabled(True)

            self.reactor._iterate(fromqt=True)

        log.callWithLogger(w, _read)

    def write(self):
        """
        The Twisted documentation for doWrite:

        A result that is true (which will be a negative number or an exception instance) indicates that the
        connection was lost. A false result implies the connection is still there; a result of 0 indicates no write
        was done, and a result of None indicates that a write was done.

        :return: None
        """
        if not self.watcher:
            return
        # see above
        w = self.watcher

        # noinspection PyProtectedMember
        def _write():
            self.notifier.setEnabled(False)
            try:
                data = w.doWrite()
            except:
                log.err()
                self.reactor._disconnectSelectable(w, sys.exc_info()[1], False)
            else:
                if data:
                    self.reactor._disconnectSelectable(w, data, True)
                elif self.watcher:
                    self.notifier.setEnabled(True)

            self.reactor._iterate(fromqt=True)

        log.callWithLogger(w, _write)


# Use kqreactor for MacOS
# (ht: Tomas Touceda / LEAP)

ReactorSuperclass = posixbase.PosixReactorBase

if runtime.platform.isMacOSX():
    from twisted.internet import kqreactor

    ReactorSuperclass = kqreactor.KQueueReactor


# noinspection PyCallByClass
# class QtReactor(posixbase.PosixReactorBase):
# noinspection PyCallByClass
class QtReactor(ReactorSuperclass):
    implements(IReactorFDSet)

    def __init__(self):
        self._reads = set()
        self._writes = set()
        self._notifiers = {}
        self._timer = QtCore.QTimer()
        self._timer.setSingleShot(True)
        QtCore.QObject.connect(self._timer, QtCore.SIGNAL("timeout()"), self.iterate)

        # noinspection PyArgumentList
        if QtCore.QCoreApplication.instance() is None:
            # Application Object has not been started yet
            self.qApp = QtCore.QCoreApplication([])
            self._ownApp = True
        else:
            # noinspection PyArgumentList
            self.qApp = QtCore.QCoreApplication.instance()
            self._ownApp = False
        self._blockApp = None
        ReactorSuperclass.__init__(self)

    def _add(self, xer, primary, descriptor_type):
        """
        Private method for adding a descriptor from the event loop.

        It takes care of adding it if  new or modifying it if already added
        for another state (read -> read/write for example).
        """
        if xer not in primary:
            primary.add(xer)
            self._notifiers[xer] = TwistedSocketNotifier(None, self, xer, descriptor_type)

    def addReader(self, reader):
        """
        Add a FileDescriptor for notification of data available to read.
        """
        self._add(reader, self._reads, QtCore.QSocketNotifier.Read)

    def addWriter(self, writer):
        """
        Add a FileDescriptor for notification of data available to write.
        """
        self._add(writer, self._writes, QtCore.QSocketNotifier.Write)

    def _remove(self, xer, primary):
        """
        Private method for removing a descriptor from the event loop.

        It does the inverse job of _add, and also add a check in case of the fd
        has gone away.
        """
        if xer in primary:
            primary.remove(xer)
            notifier = self._notifiers.pop(xer)
            notifier.shutdown()

    def removeReader(self, reader):
        """
        Remove a Selectable for notification of data available to read.
        """
        self._remove(reader, self._reads)

    def removeWriter(self, writer):
        """
        Remove a Selectable for notification of data available to write.
        """
        self._remove(writer, self._writes)

    def removeAll(self):
        """
        Remove all selectables, and return a list of them.
        """
        rv = self._removeAll(self._reads, self._writes)
        return rv

    def getReaders(self):
        return list(self._reads)

    def getWriters(self):
        return list(self._writes)

    def callLater(self, howlong, *args, **kargs):
        rval = super(QtReactor, self).callLater(howlong, *args, **kargs)
        self.invoke_reactor()
        return rval

    def invoke_reactor(self):
        self._timer.stop()
        self._timer.setInterval(0)
        self._timer.start()

    def _iterate(self, delay=None, fromqt=False):
        """
        See twisted.internet.interfaces.IReactorCore.iterate.
        """
        self.runUntilCurrent()
        self.doIteration(delay, fromqt)

    iterate = _iterate

    def doIteration(self, delay=None, fromqt=False):
        """
        This method is called by a Qt timer or by network activity
        on a file descriptor
        """
        if not self.running and self._blockApp:
            self._blockApp.quit()
        self._timer.stop()
        delay = max(delay, 1)
        if not fromqt:
            self.qApp.processEvents(QtCore.QEventLoop.AllEvents, delay * 1000)
        if self.timeout() is None:
            timeout = 0.1
        elif self.timeout() == 0:
            timeout = 0
        else:
            timeout = self.timeout()
        self._timer.setInterval(timeout * 1000)
        self._timer.start()

    # noinspection PyPep8Naming
    def runReturn(self, installSignalHandlers=True):
        self.startRunning(installSignalHandlers=installSignalHandlers)
        self.invoke_reactor()

    # noinspection PyPep8Naming
    def run(self, installSignalHandlers=True):
        if self._ownApp:
            self._blockApp = self.qApp
        else:
            self._blockApp = QtCore.QEventLoop()
        self.runReturn()
        self._blockApp.exec_()


class QtEventReactor(QtReactor):
    # noinspection PyUnusedLocal
    def __init__(self, *args, **kwargs):
        self._events = {}
        super(QtEventReactor, self).__init__()

    def add_event(self, event, fd, action):
        """
        Add a new win32 event to the event loop.
        """
        self._events[event] = (fd, action)

    def remove_event(self, event):
        """
        Remove an event.
        """
        if event in self._events:
            del self._events[event]

    def do_events(self):
        handles = self._events.keys()
        if len(handles) > 0:
            val = None
            while val != WAIT_TIMEOUT:
                val = MsgWaitForMultipleObjects(handles, 0, 0,
                                                QS_ALLINPUT | QS_ALLEVENTS)
                if WAIT_OBJECT_0 <= val < WAIT_OBJECT_0 + len(handles):
                    event_id = handles[val - WAIT_OBJECT_0]
                    if event_id in self._events:
                        fd, action = self._events[event_id]
                        log.callWithLogger(fd, self._run_action, action, fd)
                elif val == WAIT_TIMEOUT:
                    pass
                else:
                    # print 'Got an unexpected return of %r' % val
                    return

    # noinspection PyBroadException
    def _run_action(self, action, fd):
        try:
            closed = getattr(fd, action)()
        except:
            closed = sys.exc_info()[1]
            log.deferr()

        if closed:
            self._disconnectSelectable(fd, closed, action == 'doRead')

    def timeout(self):
        t = super(QtEventReactor, self).timeout()
        return min(t, 0.01)

    def iterate(self, delay=None):
        """See twisted.internet.interfaces.IReactorCore.iterate.
        """
        self.runUntilCurrent()
        self.do_events()
        self.doIteration(delay)


def posixinstall():
    """
    Install the Qt reactor.
    """
    p = QtReactor()
    from twisted.internet.main import installReactor

    installReactor(p)


def win32install():
    """
    Install the Qt reactor.
    """
    p = QtEventReactor()
    from twisted.internet.main import installReactor

    installReactor(p)


if runtime.platform.getType() == 'win32':
    from win32event import (WAIT_OBJECT_0, WAIT_TIMEOUT,
                            QS_ALLINPUT, QS_ALLEVENTS)

    install = win32install
else:
    install = posixinstall

__all__ = ["install"]
