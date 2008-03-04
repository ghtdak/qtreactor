# Copyright (c) 2001-2008 Twisted Matrix Laboratories.
# See LICENSE for details.


"""
This module provides support for Twisted to interact with the PyQt mainloop.

In order to use this support, simply do the following::

    |  import qt4reactor
    |  qt4reactor.install()

Then use twisted.internet APIs as usual.  The other methods here are not
intended to be called directly.

API Stability: stable

Maintainer: U{Itamar Shtull-Trauring<mailto:twisted@itamarst.org>}
Port to QT4: U{Gabe Rudy<mailto:rudy@goldenhelix.com>}
"""

__all__ = ['install']


import sys

from zope.interface import implements

from PyQt4.QtCore import QSocketNotifier, QObject, SIGNAL, QTimer, QCoreApplication

from twisted.internet.interfaces import IReactorFDSet
from twisted.python import log
from twisted.internet.posixbase import PosixReactorBase



class TwistedSocketNotifier(QSocketNotifier):
    """
    Connection between an fd event and reader/writer callbacks.
    """

    def __init__(self, reactor, watcher, type):
        QSocketNotifier.__init__(self, watcher.fileno(), type)
        self.reactor = reactor
        self.watcher = watcher
        self.fn = None
        if type == QSocketNotifier.Read:
            self.fn = self.read
        elif type == QSocketNotifier.Write:
            self.fn = self.write
        QObject.connect(self, SIGNAL("activated(int)"), self.fn)


    def shutdown(self):
        QObject.disconnect(self, SIGNAL("activated(int)"), self.fn)
        self.setEnabled(0)
        self.fn = self.watcher = None


    def read(self, sock):
        w = self.watcher
        def _read():
            why = None
            try:
                why = w.doRead()
            except:
                log.err()
                why = sys.exc_info()[1]
            if why:
                self.reactor._disconnectSelectable(w, why, True)
        log.callWithLogger(w, _read)
        self.reactor.simulate()


    def write(self, sock):
        w = self.watcher
        def _write():
            why = None
            self.setEnabled(0)
            try:
                why = w.doWrite()
            except:
                log.err()
                why = sys.exc_value
            if why:
                self.reactor._disconnectSelectable(w, why, False)
            elif self.watcher:
                self.setEnabled(1)
        log.callWithLogger(w, _write)
        self.reactor.simulate()



class QTReactor(PosixReactorBase):
    """
    Qt based reactor.
    """
    implements(IReactorFDSet)

    # Reference to a DelayedCall for self.crash() when the reactor is
    # entered through .iterate()
    _crashCall = None

    _timer = None

    def __init__(self, app=None):
        self._reads = {}
        self._writes = {}
        if app is None:
            """ QCoreApplication doesn't require X or other GUI
            environment """
            app = QCoreApplication([])
        self.qApp = app
        PosixReactorBase.__init__(self)
        self.addSystemEventTrigger('after', 'shutdown', self.cleanup)


    def addReader(self, reader):
        if not reader in self._reads:
            self._reads[reader] = TwistedSocketNotifier(self, reader,
                                                       QSocketNotifier.Read)


    def addWriter(self, writer):
        if not writer in self._writes:
            self._writes[writer] = TwistedSocketNotifier(self, writer,
                                                        QSocketNotifier.Write)


    def removeReader(self, reader):
        if reader in self._reads:
            self._reads[reader].shutdown()
            del self._reads[reader]


    def removeWriter(self, writer):
        if writer in self._writes:
            self._writes[writer].shutdown()
            del self._writes[writer]


    def removeAll(self):
        return self._removeAll(self._reads, self._writes)


    def getReaders(self):
        return self._reads.keys()


    def getWriters(self):
        return self._writes.keys()


    def simulate(self):
        if self._timer is not None:
            self._timer.stop()
            #del self._timer
            #self._timer = None

        if not self.running:
            self.qApp.exit()
            return
        self.runUntilCurrent()

        if self._crashCall is not None:
            self._crashCall.reset(0)

        timeout = self.timeout()
        if timeout is None:
            timeout = 1.0
        timeout = min(timeout, 0.1) * 1010

        if self._timer is None:
            self._timer = QTimer()
            QObject.connect(self._timer, SIGNAL("timeout()"), self.simulate)
        self._timer.start(timeout)
        
    """ need this to update when simulate is called back in
    case its immediate (or sooner) """         
    def callLater(self,howlong, *args, **kargs):
        rval = super(QTReactor,self).callLater(howlong, *args, **kargs)
        QTimer.singleShot(0,self.simulate)
        return rval    

    def cleanup(self):
        if self._timer is not None:
            self._timer.stop()
            self._timer = None


    def iterate(self, delay=0.0):
        self._crashCall = self.callLater(delay, self._crash)
        self.run()


    def mainLoop(self):
        self.simulate()
        self.qApp.exec_()


    def _crash(self):
        if self._crashCall is not None:
            if self._crashCall.active():
                self._crashCall.cancel()
            self._crashCall = None
        self.running = False



def install(app=None):
    """
    Configure the twisted mainloop to be run inside the qt mainloop.
    """
    from twisted.internet import main
    reactor = QTReactor(app=app)
    main.installReactor(reactor)
