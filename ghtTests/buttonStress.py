from __future__ import print_function
import sys

import PyQt4.QtCore as QtCore
import PyQt4.QtScript as QtScript
import PyQt4.QtGui as QtGui

app = QtGui.QApplication(sys.argv)

from twisted.application import reactors
reactors.installReactor('qt4')

from twisted.internet import reactor, task
from twisted.python import log

log.startLogging(sys.stdout)


class DoNothing(QtCore.QObject):
    def __init__(self):
        self.count = 0
        self.looping = False
        task.LoopingCall(self.print_stat).start(1.0)
        QtCore.QObject.__init__(self)

    def do_something(self):
        if not self.looping:
            return

        self.count += 1
        reactor.callLater(0.003, self.do_something)

    def button_click(self):
        if self.looping:
            self.looping = False
            log.msg('looping stopped....')
        else:
            self.looping = True
            self.do_something()
            log.msg('looping started....')

    def print_stat(self):
        log.msg(' c: ' + str(self.count))


t = DoNothing()

engine = QtScript.QScriptEngine()

button = QtGui.QPushButton()
scriptButton = engine.newQObject(button)
engine.globalObject().setProperty("button", scriptButton)

app.connect(button, QtCore.SIGNAL("clicked()"), t.button_click)

engine.evaluate("button.text = 'Hello World!'")
engine.evaluate("button.styleSheet = 'font-style: italic'")
engine.evaluate("button.show()")

# noinspection PyUnresolvedReferences
reactor.runReturn()
app.exec_()
log.msg('fell off the bottom?...')


