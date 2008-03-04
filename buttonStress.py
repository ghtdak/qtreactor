import sys
from PyQt4 import QtGui, QtScript
from PyQt4.QtCore import QTimer, SIGNAL
import qt4reactor

app = QtGui.QApplication(sys.argv)
qt4reactor.install(app)

from twisted.internet import reactor, task
from twisted.python import log
log.startLogging(sys.stdout)

class doNothing(object):
    def __init__(self):
        self.count = 0
        self.looping=False
        task.LoopingCall(self.printStat).start(5.0)
        
    def doSomething(self):
        if not self.looping: return
        self.count += 1
        reactor.callLater(0.01,self.doSomething)
        
    def buttonClick(self):
        if self.looping: 
            self.looping=False
            log.msg('looping stopped....')
        else: 
            self.looping=True
            self.doSomething()
            log.msg('looping started....')
        
    def printStat(self):
#===============================================================================
#        log.msg(' c: ' + str(self.count) + 
#                ' st: ' + str(reactor.simCount) +
#                ' rw: ' + str(reactor.rwsimCount) +
#                ' to: ' + str(reactor.tm))
#===============================================================================

        log.msg('c:' + str(self.count))

t=doNothing()

engine = QtScript.QScriptEngine()

button = QtGui.QPushButton()
scriptButton = engine.newQObject(button)
engine.globalObject().setProperty("button", scriptButton)

app.connect(button, SIGNAL("clicked()"), t.buttonClick)

engine.evaluate("button.text = 'Hello World!'")
engine.evaluate("button.styleSheet = 'font-style: italic'")
engine.evaluate("button.show()")

reactor.run()
log.msg('fell off the bottom?...')


