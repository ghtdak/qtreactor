import sys

import sys
from PyQt4 import QtGui, QtScript
from PyQt4.QtCore import QTimer, SIGNAL

def testReactor():
    print 'tick...'

def testReactor2():
    print 'click...'
    
reactorInstalled = False

localReactor = None
    
def buttonClick():
    if reactorInstalled:
        localReactor.callLater(0.0,testReactor2)
    else:
        doReactorInstall()

def doReactorInstall():
    global reactorInstalled
    if reactorInstalled:
        reactor.callLater(0.0,testReactor2)
        return
    else:
        reactorInstalled=True
    print "installing reactor"
    import qt4reactor
    qt4reactor.install(app)
    from twisted.internet import reactor, task
    from twisted.python import log
    log.startLogging(sys.stdout)
    task.LoopingCall(testReactor).start(1.0)
    from twisted.internet import reactor, task
    reactor.returnRun()
    log.msg('returning from run')
    """ should really figure out what happens when
    reactor is imported methinks """
    global localReactor
    localReactor=reactor

app = QtGui.QApplication(sys.argv)

engine = QtScript.QScriptEngine()

button = QtGui.QPushButton()
scriptButton = engine.newQObject(button)
engine.globalObject().setProperty("button", scriptButton)

app.connect(button, SIGNAL("clicked()"), buttonClick)

engine.evaluate("button.text = 'Hello World!'")
engine.evaluate("button.styleSheet = 'font-style: italic'")
engine.evaluate("button.show()")
    
sys.exit(app.exec_())

