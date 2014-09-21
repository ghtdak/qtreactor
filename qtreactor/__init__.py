"""
Twisted / Qt mainloop integration.  PyQt4 and PySide are supported
in separate (virtually identical) modules.  Specifying the reactor
using Twisted's plug-in mechanism constructs the requested reactor
and avoids name collision if both PyQt and PySide are installed.

Before any other Twisted code is run, invoke:

    |  app = QApplication(sys.argv) # your code to init Qt
    |  from twisted.application import reactors
    |  reactors.installReactor('qt4')

or

    |  app = QApplication(sys.argv) # your code to init Qt
    |  from twisted.application import reactors
    |  reactors.installReactor('pyside')

alternatively (gui example):

    |  app = PyQt4.QtGui(sys.argv) # your code to init Qt
    |  from twisted.application import reactors
    |  qt4reactor.install

Then use twisted.internet APIs as usual.  The other methods here are not
intended to be called directly.

If you don't instantiate a QApplication or QCoreApplication prior to
installing the reactor, a QCoreApplication will be constructed
by the reactor.  QCoreApplication does not require a GUI so trial testing
can occur normally.

Twisted can be initialized after QApplication.exec_() with a call to
reactor.runReturn().  calling reactor.stop() will unhook twisted but
leave your Qt application running

API Stability: stable

Maintainer: U{Glenn H Tarbox, PhD<mailto:glenn@tarbox.org>}

Previous maintainer: U{Itamar Shtull-Trauring<mailto:twisted@itamarst.org>}
Original port to QT4: U{Gabe Rudy<mailto:rudy@goldenhelix.com>}
Subsequent port by therve
"""

#__ALL__=['pyqt4reactor','pyside4reactor' ,'qt4base']
