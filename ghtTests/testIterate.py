from __future__ import print_function

import sys

from PySide import QtGui, QtScript
from PySide.QtCore import SIGNAL

app = QtGui.QApplication(sys.argv)

from qtreactor import pyqt4reactor

pyqt4reactor.install()

from twisted.internet import reactor, task
from twisted.python import log

log.startLogging(sys.stdout)


def test_reactor():
    print('tick...')


def button_click():
    print('click...')
    reactor.iterate(5.0)
    print('click return')


engine = QtScript.QScriptEngine()

button = QtGui.QPushButton()
scriptButton = engine.newQObject(button)
engine.globalObject().setProperty("button", scriptButton)

app.connect(button, SIGNAL("clicked()"), button_click)

engine.evaluate("button.text = 'Hello World!'")
engine.evaluate("button.styleSheet = 'font-style: italic'")
engine.evaluate("button.show()")

task.LoopingCall(test_reactor).start(1.0)
reactor.run()
log.msg('fell off the bottom?...')
