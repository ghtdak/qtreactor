from __future__ import print_function, absolute_import

import sys

import PyQt4.QtGui as QtGui
import PyQt4.QtScript as QtScript
from PyQt4.QtCore import SIGNAL

app = QtGui.QApplication(sys.argv)

from qtreactor import pyqt4reactor

pyqt4reactor.install()


class DoNothing(object):
    def __init__(self):
        self.count = 0
        self.running = False

    def button_click(self):
        if not self.running:
            from twisted.scripts import trial
            trial.run()


def run():

    t = DoNothing()

    engine = QtScript.QScriptEngine()

    button = QtGui.QPushButton()
    button = engine.newQObject(button)
    engine.globalObject().setProperty("button", button)

    app.connect(button, SIGNAL("clicked()"), t.button_click)

    engine.evaluate("button.text = 'Do Twisted Gui Trial'")
    engine.evaluate("button.styleSheet = 'font-style: italic'")
    engine.evaluate("button.show()")

    app.exec_()
    print('fell off the bottom?...')
