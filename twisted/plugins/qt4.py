# Copyright (c) 2001-2010 Twisted Matrix Laboratories.
# see LICENSE for details


from twisted.application.reactors import Reactor

qt4 = Reactor('qt4', 'qt4reactor', 'PyQt4 integration reactor')
pyqt4 = Reactor('pyqt4', 'qtreactor.pyqt4reactor', 'PyQt4 integration reactor')
pyside4 = Reactor('pyside4', 'qtreactor.pyside4reactor', 'PySide4 integration reactor')
qt4bad = Reactor('qt4bad', 'qt4reactor_bad', 'Qt4 broken reactor')
