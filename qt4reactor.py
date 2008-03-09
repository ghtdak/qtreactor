# Copyright (c) 2001-2008 Twisted Matrix Laboratories.
# See LICENSE for details.


"""
This module provides support for Twisted to be driven by the Qt mainloop.

In order to use this support, simply do the following::

    |  import qt4reactor
    |  qt4reactor.install()

Then use twisted.internet APIs as usual.  The other methods here are not
intended to be called directly.

API Stability: stable

Maintainer: U{Glenn H Tarbox, PhD<mailto:glenn@tarbox.org>}

Previous maintainer: U{Itamar Shtull-Trauring<mailto:twisted@itamarst.org>}
Original port to QT4: U{Gabe Rudy<mailto:rudy@goldenhelix.com>}
Subsequent port by therve
"""

__all__ = ['install']


import sys, time

from zope.interface import implements

from PyQt4.QtCore import QSocketNotifier, QObject, SIGNAL, QTimer, QCoreApplication
from PyQt4.QtCore import QEventLoop, QAbstractEventDispatcher

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
        self.setEnabled(False)
        self.fn = self.watcher = None


    def read(self, sock):
        w = self.watcher
        #self.setEnabled(False)                
        def _read():
            why = None
            try:
                why = w.doRead()
            except:
                log.err()
                why = sys.exc_info()[1]
            if why:
                self.reactor._disconnectSelectable(w, why, True)
            elif self.watcher:
                pass
                #self.setEnabled(True)
        #self.reactor.addReadWrite((w, _read))
        log.callWithLogger(w, _read)
        #self.reactor.pingSimulate()


    def write(self, sock):
        w = self.watcher
        self.setEnabled(False)
        def _write():
            why = None
            try:
                why = w.doWrite()
            except:
                log.err()
                why = sys.exc_info()[1]
            if why:
                self.reactor._disconnectSelectable(w, why, False)
            elif self.watcher:
                self.setEnabled(True)
        #self.reactor.addReadWrite((w, _write))
        log.callWithLogger(w, _write)
        #self.reactor.pingSimulate()
        

class fakeApplication(QEventLoop):
    def __init__(self):
        QEventLoop.__init__(self)
        
    def go(self):
        #print 'entering exec_'
        QEventLoop.exec_(self)
        
class signalCatcher(QObject):
    def __init__(self):
        QObject.__init__(self)
        
    def callLaterSignal(self):
        self.emit(SIGNAL("twistedEvent"),'c')

class QTReactor(PosixReactorBase):
    """
    Qt based reactor.
    """
    implements(IReactorFDSet)

    # Reference to a DelayedCall for self.crash() when the reactor is
    # entered through .iterate()
    _crashCall = None

    _timer = None

    def __init__(self):
        self._reads = {}
        self._writes = {}
        self._readWriteQ=[]
        self._timer=QTimer()
        self._timer.setSingleShot(True)
        self.qApp = QCoreApplication.instance()
        self._blockApp = None
        self._signalCatcher = signalCatcher()
        
        """ some debugging instrumentation """
        self._doSomethingCount=0
        
        PosixReactorBase.__init__(self)

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
    
    def callLater(self,howlong, *args, **kargs):
        rval = super(QTReactor,self).callLater(howlong, *args, **kargs)
        #self.qApp.emit(SIGNAL("twistedEvent"),'c')
        self._signalCatcher.callLaterSignal()
        return rval
    
    def crash(self):
        super(QTReactor,self).crash()
        
    def pingWatchdog(self):
        self._watchdog.start(2000)
        
    def watchdogTimeout(self):
        print '****************** Watchdog Death ****************'
        self.crash()

    def cleanup(self):
        print 'cleanup'
        self.iterate() # cleanup pending events?
        self.running=False
        #self.iterate() # cleanup pending events?
        self.qApp.emit(SIGNAL("twistedEvent"),'shutdown')

    def toxic_Reiterate(self,delay=0.0):
        """
        WARNING: this re-entrant iterate CAN AND WILL
        have dire and unintended consequences for all those
        who attempt usage without the proper clearances.
        """
        app=QCoreApplication.instance()
        endTime = delay + time.time()
        app.processEvents() # gotta do at least one
        while True:
            t = endTime - time.time()
            if t <= 0.0: return
            app.processEvents(QEventLoop.AllEvents | 
                              QEventLoop.WaitForMoreEvents,t*1010)
            
    def addReadWrite(self,t):
        self._readWriteQ.append(t)
        self.qApp.emit(SIGNAL("twistedEvent"),'fileIO')
        
    def runReturn(self, installSignalHandlers=True):
        QObject.connect(self.qApp,SIGNAL("twistedEvent"),
                        self.reactorInvocation)
        QObject.connect(self._timer, SIGNAL("timeout()"), 
                        self.reactorInvoke)
        self.startRunning(installSignalHandlers=installSignalHandlers)
        self.addSystemEventTrigger('after', 'shutdown', self.cleanup)
        self.qApp.emit(SIGNAL("twistedEvent"),'startup')
        QTimer.singleShot(101,self.slowPoll)
        self._timer.start(0)
        
    def run(self, installSignalHandlers=True):
        try:
            self._blockApp = fakeApplication()
            self.runReturn(installSignalHandlers)
            self._blockApp.go()
        finally:
            self._blockApp=None

    def slowPoll(self):
        self.qApp.emit(SIGNAL("twistedEvent"),'slowpoll')
        if self.running:
            QTimer.singleShot(101,self.slowPoll)
    
    def reactorInvocation(self):
        self._timer.setInterval(0)
        
    def reactorInvoke(self):
        self._doSomethingCount += 1
        if self.running:
            self.runUntilCurrent()
            t2 = self.timeout()
            t = self.running and t2
            if t is None: t=1.0
            self._timer.start(t*1010)
            self.doIteration(99999)
        else:
            if self._blockApp is not None:
                self._blockApp.quit()
                
    def doReactorEvent(self,delay):
        for i in self._readWriteQ:
            log.callWithLogger(i[0], i[1])
        _readWriteQ=[]
            
    doIteration = doReactorEvent
            
    def iterate(self, delay=0.0):
        #print '********************* someone called iterate...'
        self.toxic_Reiterate(delay)
        
def install():
    """
    Configure the twisted mainloop to be run inside the qt mainloop.
    """
    from twisted.internet import main
    reactor = QTReactor()
    main.installReactor(reactor)
