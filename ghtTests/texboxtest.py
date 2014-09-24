from __future__ import print_function

from PyQt4 import QtCore
from PyQt4.QtGui import *

import sys
app = QApplication(sys.argv)

import qtreactor.pyqt4reactor
qtreactor.pyqt4reactor.install()

#reactors.installReactor('pyqt4')

from twisted.internet import reactor, task

class AppForm(QMainWindow):
    def __init__(self, parent=None):
        QMainWindow.__init__(self, parent)
        self.qpingcount=0
        self.create_main_frame()

    def create_main_frame(self):        
        page = QWidget()        

        self.button = QPushButton('joy', page)
        #self.button2 = QPushButton('loop', page)
        self.edit1 = QLineEdit()
        self.edit2 = QLineEdit()

        vbox1 = QVBoxLayout()
        #vbox1.addWidget(self.button2)
        vbox1.addWidget(self.edit1)
        vbox1.addWidget(self.edit2)
        vbox1.addWidget(self.button)
        page.setLayout(vbox1)
        self.setCentralWidget(page)

        self.connect(self.button,
                     QtCore.SIGNAL("clicked()"),
                     self.clicked2)

        #self.connect(self.button2,
        #             QtCore.SIGNAL("clicked()"),
        #             self.spawnclick)

        self._timer = QtCore.QTimer()
        self._timer.setSingleShot(False)
        QtCore.QObject.connect(self._timer,
                               QtCore.SIGNAL("timeout()"),
                               self.qclick)

        self._timer.setInterval(1000)
        self._timer.start()


    def spawnclick(self):
        self.lc = task.LoopingCall(self.pingbox)
        self.lc.start(1.0)

    def clicked1(self):
        # todo, the inspector isn't happy here either
        QMessageBox.about(self, "My message box", "Text1 = %s, Text2 = %s" % (
            self.edit1.text(), self.edit2.text()))

    def qclick(self):
        self.qpingcount += 1
        self.edit1.setText(str(self.qpingcount))

    def clicked2(self):
        self.edit1.setText("die mutherfucker")
        try:
            self.lc.stop()
        except:
            pass
        finally:
            reactor.callLater(1.0, reactor.stop)

    def pingbox(self):
        self.edit2.setText(str(qtreactor.pyqt4reactor.pyqt4reactor.pingcount))


lc = None
form = None

def buildgui():
    form = AppForm()
    form.show()
    return form

if __name__ == "__main__":
    form = buildgui()
    #app.exec_()
    reactor.run()


