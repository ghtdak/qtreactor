from __future__ import print_function

import sys

from PyQt4 import QtGui, QtScript
from PyQt4 import QtCore

app = QtGui.QApplication(sys.argv)

from qtreactor import pyqt4reactor

pyqt4reactor.install()

from twisted.internet import reactor, task


class DoNothing(object):
    def __init__(self):
        self.count = 0
        self.running = False
        task.LoopingCall(self.print_stat).start(1.0)

    def button_click(self):
        if self.running:
            self.running = False
            print('CLICK: calling reactor stop...')
            reactor.stop()
            print('reactor stop called....')
        else:
            self.running = True
            print('CLICK: entering run')
            reactor.run()
            print('reactor run returned...')

    @staticmethod
    def print_stat():
        print('tick...')


t = DoNothing()

engine = QtScript.QScriptEngine()

button = QtGui.QPushButton()
scriptButton = engine.newQObject(button)
engine.globalObject().setProperty("button", scriptButton)

app.connect(button, QtCore.SIGNAL("clicked()"), t.button_click)

engine.evaluate("button.text = 'Hello World!'")
engine.evaluate("button.styleSheet = 'font-style: italic'")
engine.evaluate("button.show()")

app.exec_()
print('fell off the bottom?...')
