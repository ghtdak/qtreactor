# Copyright (c) 2001-2004 Twisted Matrix Laboratories.
# See LICENSE for details.


"""
This module provides support for Twisted to interact with the PyQt mainloop.

In order to use this support, simply do the following::

    |  from twisted.internet import qtreactor
    |  qtreactor.install()

Then use twisted.internet APIs as usual.  The other methods here are not
intended to be called directly.

API Stability: stable

Maintainer: U{Itamar Shtull-Trauring<mailto:twisted@itamarst.org>}
Port to QT4: U{Gabe Rudy<mailto:rudy@goldenhelix.com>}
"""


# System Imports
from PyQt4.QtCore import QSocketNotifier, QObject, SIGNAL, QTimer,QThread
from PyQt4.QtGui import QApplication
import sys, time

# Twisted Imports
from twisted.python import log, failure
from twisted.internet import posixbase

reads = {}
writes = {}
hasReader = reads.has_key
hasWriter = writes.has_key


class TwistedSocketNotifier(object):
    '''Connection between an fd event and reader/writer callbacks'''

    def __init__(self, reactor, watcher, type):
        self.reactor = reactor
        self.watcher = watcher
        self.fn = None
        self.qNotifier=None
        if type == QSocketNotifier.Read:
            self.fn = self.read
        elif type == QSocketNotifier.Write:
            self.fn = self.write
        reactor.callLater(0.0,self.qsocketNailup,
                          watcher.fileno(), type, self.fn)
    
    def qsocketNailup(self, fileno, type, fn):

        self.qNotifier = QSocketNotifier(fileno, type)
        QObject.connect(self.qNotifier, SIGNAL("activated(int)"), fn)

    def shutdown(self):
        if self.qNotifier != None:
            QObject.disconnect(self.qNotifier, SIGNAL("activated(int)"), self.fn)
            self.qNotifier.setEnabled(0)
        self.fn = self.watcher = None

    def read(self, sock):
        why = None
        w = self.watcher
        try:
            log.msg('reading...')
            why = w.doRead()
        except:
            why = sys.exc_info()[1]
            log.msg('Error in %s.doRead()' % w)
            log.deferr()
        if why:
            self.reactor._disconnectSelectable(w, why, True)
        self.reactor.simulate()

    def write(self, sock):
        why = None
        w = self.watcher
        self.qNotifier.setEnabled(0)
        try:
            log.msg('writing...')
            why = w.doWrite()
        except:
            why = sys.exc_value
            log.msg('Error in %s.doWrite()' % w)
            log.deferr()
        if why:
            self.reactor.removeReader(w)
            self.reactor.removeWriter(w)
            try:
                w.connectionLost(failure.Failure(why))
            except:
                log.deferr()
        elif self.watcher:
            self.setEnabled(1)
        self.reactor.simulate()


class QTReactor(posixbase.PosixReactorBase):
    """Qt based reactor."""

    # Reference to a DelayedCall for self.crash() when the reactor is
    # entered through .iterate()
    _crashCall = None

    def __init__(self, app=None):
#===============================================================================
#        self.running = 0
#===============================================================================
        posixbase.PosixReactorBase.__init__(self)
        if app is None:
            app = QApplication([])
        self.qApp = app
        self.qAppRunning=False

    def addReader(self, reader):
        if not hasReader(reader):
            log.msg("addReader...")
            reads[reader] = TwistedSocketNotifier(self, reader, QSocketNotifier.Read)

    def addWriter(self, writer):
        if not hasWriter(writer):
            log.msg("addWriter...")            
            writes[writer] = TwistedSocketNotifier(self, writer, QSocketNotifier.Write)

    def removeReader(self, reader):
        log.msg("removeReader...")
        if hasReader(reader):
            reads[reader].shutdown()
            del reads[reader]

    def removeWriter(self, writer):
        log.msg("removeWriter...")        
        if hasWriter(writer):
            writes[writer].shutdown()
            del writes[writer]

    def removeAll(self):
        return self._removeAll(reads, writes)
    
    def processQtEvents(self):
        self.qApp.processEvents()

    def simulate(self):
#===============================================================================
#        if self.running == False:
#            return
#===============================================================================

#===============================================================================
#        if not self.running:
#            self.running = 1
#            self.qApp.exit_loop()
#            return
#        self.runUntilCurrent()
#===============================================================================

        self.runUntilCurrent()

        timeout = self.timeout()
        if timeout is None:
            timeout = 1.0
        timeout = min(timeout, 0.1) * 1010
        
        QTimer.singleShot(timeout,self.simulate)

    def cleanup(self):
        pass

    """ need this to update when simulate is called back in
    case its immediate or sooner """         
    def callLater(self,howlong, *args, **kargs):
        rval = super(QTReactor,self).callLater(howlong, *args, **kargs)
        timeout = self.timeout() * 1010
        if self.running:
            QTimer.singleShot(timeout,self.simulate)
        return rval

    def iterate(self, delay=0.0):
        #assert self.running, " call reactor run first"
        #log.msg(channel='system', event='iteration', reactor=self)
        #self._crashCall = self.callLater(delay, self.crash)
        endtime = time.time() + delay
        self.runUntilCurrent()
        self.processQtEvents()
        while time.time() < endtime:
            self.runUntilCurrent()
            self.processQtEvents()
        
    def initialize(self):
        log.msg('************** qt4.initialize() ******************')        
        self.qAppRunning=True
        self.simulate()
        
    def run(self,installSignalHandlers=1):
        log.msg('************** qt4.run() ******************')
        self.startRunning(installSignalHandlers=installSignalHandlers)
        if not self.qAppRunning:
            self.qApp.exec_()
            
    def stop(self):
        self.qApp.quit()
        self.removeAll()        
        super(QTReactor,self).stop()
        self.qAppRunning=False
            
    def crash(self):
        self.qApp.quit()
        self.removeAll()        
        super(QTReactor,self).crash()
        self.qAppRunning=False
#===============================================================================
#        if self._crashCall is not None:
#            if self._crashCall.active():
#                self._crashCall.cancel()
#            self._crashCall = None
#        self.running = False
#===============================================================================


def install(app=None):
    """Configure the twisted mainloop to be run inside the qt mainloop.
    """
    from twisted.internet import main
    class runThread(QThread):
            def __init__(self,app):
                QThread.__init__(self)
                self.app=app
                
            def run(self):
                reactor = QTReactor(app=self.app)
                main.installReactor(reactor)
                QTimer.singleShot(0,reactor.initialize)
                

    t=runThread(app)
    t.run()
    t.wait()
    print '************* qt4 install complete *******************'
    
__all__ = ['install']
