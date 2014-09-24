#
#http://stackoverflow.com/questions/4155052/how-to-display-a-message-box-on-pyqt4
#

from PyQt4 import QtCore
from PyQt4.QtGui import *
import sys
app = QApplication(sys.argv)
import qtreactor.pyqt4reactor
qtreactor.pyqt4reactor.install()

from twisted.internet import reactor, task

class AppForm(QMainWindow):
    def __init__(self, parent=None):
        QMainWindow.__init__(self, parent)
        self.create_main_frame()
        self.qpingcount=0

    def create_main_frame(self):        
        page = QWidget()        

        self.button = QPushButton('joy', page)
        self.b2 = QPushButton('spawn', page)
        self.edit1 = QLineEdit()
        self.edit2 = QLineEdit()

        vbox1 = QVBoxLayout()
        vbox1.addWidget(self.b2)
        vbox1.addWidget(self.edit1)
        vbox1.addWidget(self.edit2)
        vbox1.addWidget(self.button)
        page.setLayout(vbox1)
        self.setCentralWidget(page)

        self.connect(self.button,
                     QtCore.SIGNAL("clicked()"),
                     self.clicked)

        self.connect(self.b2,
                     QtCore.SIGNAL("clicked()"),
                    self.spawnclick)

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

    def clicked(self):
        QMessageBox.about(self, "My message box", "Text1 = %s, Text2 = %s" % (
            self.edit1.text(), self.edit2.text()))

    def qclick(self):
        self.qpingcount += 1
        self.edit1.setText(str(self.qpingcount))



if __name__ == "__main__":
    import sys
    form = AppForm()
    form.show()
    reactor.run()
    #app.exec_()
