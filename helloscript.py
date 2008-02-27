import sys
sys.path.insert(0,'/home/tarbox/workspace/external/IbPy')
sys.path.insert(0,'/home/tarbox/workspace/pyWorking/ght/playIbpy')

import sys
from PyQt4 import QtGui, QtScript
from PyQt4.QtCore import QTimer, SIGNAL

#from twisted.internet import reactor

def testReactor():
    print 'tick...'

def doReactorInstall():
    global reactorInstalled
    if reactorInstalled:
        return
    else:
        reactorInstalled=True
    print "installing reactor"
    from Core import qt4reactor
    qt4reactor.install(app)
    from twisted.internet import reactor, task
    from twisted.python import log
    log.startLogging(sys.stdout)
    task.LoopingCall(testReactor).start(1.0)
    from twisted.internet import reactor, task
    import generatorSupport
    reactor.callWhenRunning(generatorSupport.doTest)
    reactor.returnRun()
    log.msg('returning from run')

app = QtGui.QApplication(sys.argv)

engine = QtScript.QScriptEngine()

button = QtGui.QPushButton()
scriptButton = engine.newQObject(button)
engine.globalObject().setProperty("button", scriptButton)

app.connect(button, SIGNAL("clicked()"), doReactorInstall)

engine.evaluate("button.text = 'Hello World!'")
engine.evaluate("button.styleSheet = 'font-style: italic'")
engine.evaluate("button.show()")
    
reactorInstalled = False

#QTimer.singleShot(10,doReactorInstall)

#reactor.run()

sys.exit(app.exec_())

