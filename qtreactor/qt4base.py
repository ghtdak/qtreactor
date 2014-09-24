# Copyright (c) 2001-2011 Twisted Matrix Laboratories.
# See LICENSE for details.
"""
This module provides support for Twisted to be driven by the Qt mainloop.

In order to use this support, simply do the following::
    |  app = QApplication(sys.argv) # your code to init Qt
    |  import qt4reactor
    |  qt4reactor.install()

alternatively:

    |  from twisted.application import reactors
    |  reactors.installReactor('qt4')

Then use twisted.internet APIs as usual.  The other methods here are not
intended to be called directly.

If you don't instantiate a QApplication or QCoreApplication prior to
installing the reactor, a QCoreApplication will be constructed
by the reactor.  QCoreApplication does not require a GUI so trial testing
can occur normally.

Twisted can be initialized after QApplication.exec_() with a call to
reactor.runReturn().  calling reactor.stop() will unhook twisted but
leave your Qt application running

API Stability: stable

Maintainer: U{Glenn H Tarbox, PhD<mailto:glenn@tarbox.org>}

Previous maintainer: U{Itamar Shtull-Trauring<mailto:twisted@itamarst.org>}
Original port to QT4: U{Gabe Rudy<mailto:rudy@goldenhelix.com>}
Subsequent port by therve
"""

from __future__ import print_function, absolute_import

import sys

if __name__ == '__main__':
    from twisted.application import reactors

    reactors.installReactor('pyqt4')

from zope.interface import implements
from twisted.internet.interfaces import IReactorFDSet
from twisted.python import log, runtime
from twisted.internet import posixbase

from qtreactor import qtreactor_config

if qtreactor_config.get_qt_name() == "PyQt4":
    from PyQt4 import QtCore
elif qtreactor_config.get_qt_name() == "PySide":
    from PySide import QtCore
else:
    raise Exception("Must Have PyQt4 or PySide")


# noinspection PyBroadException,PyProtectedMember
class TwistedSocketNotifier(QtCore.QObject):
    """
    Connection between an fd event and reader/writer callbacks.
    """

    def __init__(self, parent, qt_reactor, watcher, socket_type):
        QtCore.QObject.__init__(self, parent)
        self.qt_reactor = qt_reactor
        self.watcher = watcher
        fd = watcher.fileno()
        self.notifier = QtCore.QSocketNotifier(fd, socket_type, parent)
        self.notifier.setEnabled(True)
        if socket_type == QtCore.QSocketNotifier.Read:
            self.fn = self.read
        else:
            self.fn = self.write
        QtCore.QObject.connect(self.notifier,
                               QtCore.SIGNAL("activated(int)"),
                               self.fn)

    def shutdown(self):
        self.notifier.setEnabled(False)
        self.disconnect(self.notifier, QtCore.SIGNAL("activated(int)"), self.fn)
        self.fn = self.watcher = None
        self.notifier.deleteLater()
        self.deleteLater()

    # noinspection PyUnusedLocal
    def read(self, fd):
        self.notifier.setEnabled(False)
        if not self.watcher:
            return
        w = self.watcher
        # doRead can cause self.shutdown to be called so keep a
        # reference to self.watcher

        def _read():
            try:
                data = w.doRead()
                if data:
                    self.qt_reactor._disconnectSelectable(w, data, True)
                elif self.watcher:
                    self.notifier.setEnabled(True)
            except:
                log.err()
                self.qt_reactor._disconnectSelectable(w, sys.exc_info()[1], False)
            self.qt_reactor._iterate(None, fromqt=True)

        log.callWithLogger(w, _read)

    # noinspection PyUnusedLocal
    def write(self, sock):
        self.notifier.setEnabled(False)
        if not self.watcher:
            return
        w = self.watcher

        def _write():
            try:
                data = w.doWrite()
                if data:
                    self.qt_reactor._disconnectSelectable(w, data, False)
                elif self.watcher:
                    self.notifier.setEnabled(True)
            except:
                log.err()
                self.qt_reactor._disconnectSelectable(w, sys.exc_info()[1], False)
            self.qt_reactor._iterate(None, fromqt=True)

        log.callWithLogger(w, _write)


# noinspection PyUnusedLocal
def msg_stub(msg_type, msg):
    pass


def msg_blast(msg_type, msg):
    log.msg("Qt says: ", msg_type, msg)


class QtReactor(posixbase.PosixReactorBase):
    implements(IReactorFDSet)

    def __init__(self):
        self._reads = {}
        self._writes = {}
        self._notifiers = {}
        self._timer = QtCore.QTimer()
        self._timer.setSingleShot(True)
        QtCore.QObject.connect(self._timer,
                               QtCore.SIGNAL("timeout()"),
                               self._qt_timeout)

        # noinspection PyArgumentList,PyArgumentList
        if QtCore.QCoreApplication.instance() is None:
            # Application Object has not been started yet
            self.qApp = QtCore.QCoreApplication([])
            self._ownApp = True
        else:
            self.qApp = QtCore.QCoreApplication.instance()
            self._ownApp = False
        self._blockApp = None

        QtCore.qInstallMsgHandler(msg_blast)

        super(QtReactor, self).__init__()

    def _add(self, xer, primary, select_rw):
        """
        Private method for adding a descriptor from the event loop.

        It takes care of adding it if  new or modifying it if already added
        for another state (read -> read/write for example).
        """
        if xer not in primary:
            primary[xer] = TwistedSocketNotifier(None, self, xer, select_rw)

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

    # noinspection PyMethodMayBeStatic
    def _remove(self, xer, primary):
        """
        Private method for removing a descriptor from the event loop.

        It does the inverse job of _add, and also add a check in case of the fd
        has gone away.
        """
        if xer in primary:
            notifier = primary.pop(xer)
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
        return self._reads.keys()

    def getWriters(self):
        return self._writes.keys()

    def callLater(self, howlong, *args, **kargs):
        rval = super(QtReactor, self).callLater(howlong, *args, **kargs)
        self.invoke_reactor()
        return rval

    def invoke_reactor(self):
        self._timer.stop()
        self._timer.setInterval(0)
        self._timer.start()

    def _qt_timeout(self):
        self._iterate(None, True)

    def _iterate(self, delay, fromqt):
        """
        See twisted.internet.interfaces.IReactorCore.iterate.
        """
        self.runUntilCurrent()
        self._do_iteration(delay, fromqt)

    def doIteration(self, delay=None):
        self._do_iteration(delay, False)

    def _do_iteration(self, delay, fromqt):
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

    def runReturn(self, installSignalHandlers=True):
        self.startRunning(installSignalHandlers=installSignalHandlers)
        self.invoke_reactor()

    def run(self, installSignalHandlers=True):
        if self._ownApp:
            self._blockApp = self.qApp
        else:
            self._blockApp = QtCore.QEventLoop()
        self.runReturn()
        self._blockApp.exec_()


class QtEventReactor(QtReactor):
    def __init__(self, *args, **kwargs):
        self._events = {}
        super(QtEventReactor, self).__init__()

    def addEvent(self, event, fd, action):
        """
        Add a new win32 event to the event loop.
        """
        self._events[event] = (fd, action)

    def removeEvent(self, event):
        """
        Remove an event.
        """
        if event in self._events:
            del self._events[event]

    def doEvents(self):
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
                        log.callWithLogger(fd, self._runAction, action, fd)
                elif val == WAIT_TIMEOUT:
                    pass
                else:
                    # print 'Got an unexpected return of %r' % val
                    return

    # noinspection PyBroadException
    def _runAction(self, action, fd):
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
        self.doEvents()
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
    # noinspection PyUnresolvedReferences
    from win32event import (WAIT_OBJECT_0, WAIT_TIMEOUT,
                            QS_ALLINPUT, QS_ALLEVENTS)

    install = win32install
else:
    install = posixinstall

if __name__ == '__main__':
    from twisted.internet import reactor

    print("ran with: ", reactor.__module__)

    trialpath = '/usr/local/bin/trial'
    trial = open(trialpath, 'r').read()

    import contextlib

    # noinspection PyProtectedMember
    @contextlib.contextmanager
    def redirect_argv(trials):
        sys._argv = sys.argv[:]
        sys.argv[:] = trials
        yield
        sys.argv[:] = sys._argv

    with redirect_argv([trialpath,
                        'twisted.test.test_ftp',
                        'twisted.test.test_internet']):
        exec trial
        print("ran with: ", reactor.__module__)

__all__ = ["install"]
