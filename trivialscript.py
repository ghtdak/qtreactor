import sys

import sys
from PyQt4 import QtGui, QtScript
from PyQt4.QtCore import QTimer, SIGNAL
import qt4reactor

def testReactor():
    print 'tick...'

#===============================================================================
# app = QtGui.QApplication(sys.argv)
# print "installing reactor"
# qt4reactor.install(app)
#===============================================================================

from twisted.application import reactors
reactors.installReactor('qt4')

from twisted.internet import reactor, task
from twisted.python import log
log.startLogging(sys.stdout)
from twisted.internet import reactor, task

def buildGui():
    engine = QtScript.QScriptEngine()
    
    button = QtGui.QPushButton()
    scriptButton = engine.newQObject(button)
    engine.globalObject().setProperty("button", scriptButton)
    
    def buttonClick():
        localReactor.callLater(0.0,testReactor2)
    
    app.connect(button, SIGNAL("clicked()"), buttonClick)
    
    engine.evaluate("button.text = 'Hello World!'")
    engine.evaluate("button.styleSheet = 'font-style: italic'")
    engine.evaluate("button.show()")

task.LoopingCall(testReactor).start(1.0)
#reactor.callWhenRunning(buildGui)
reactor.run()
log.msg('fell off the bottom?...')

#sys.exit(app.exec_())

