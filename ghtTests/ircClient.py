from __future__ import print_function

from qtreactor import pyqt4reactor

from PyQt4 import QtGui

app = QtGui.QApplication(sys.argv)
pyqt4reactor.install()

from twisted.words.protocols import irc
from twisted.internet import reactor, protocol

import sys


# noinspection PyClassHasNoInit
class IRCCore(irc.IRCClient):
    nickname = 'dosdsdssd'

    def connectionMade(self):
        self.nickname = self.factory.window.nickName.text().encode('ascii')
        self.factory.window.protocol = self
        irc.IRCClient.connectionMade(self)
        self.log('connected!!')

    def connectionLost(self, reason):
        self.log('disconnected... :( %s' % reason)

    def signedOn(self):
        charname = self.factory.window.channelName.text().encode('ascii')
        self.join(charname)

    def joined(self, channel):
        self.log('joined %s' % channel)

    def privmsg(self, user, channel, msg):
        self.log('%s %s %s' % (user, channel, msg))

    def action(self, user, channel, msg):
        self.log('action: %s %s %s' % (user, channel, msg))

    def log(self, log_str):
        self.factory.window.view.addItem(log_str)


class IRCCoreFactory(protocol.ClientFactory):
    protocol = IRCCore

    def __init__(self, window):
        self.window = window

    def clientConnectionLost(self, connector, reason):
        # reconnect to server if lose connection
        connector.connect()

    def clientConnectionFailed(self, connector, reason):
        print('connection failed! :(', reason)
        reactor.stop()


class MainWindow(QtGui.QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()

        layout = QtGui.QHBoxLayout()

        layout.addWidget(QtGui.QLabel('Server:'))

        self.serverName = QtGui.QLineEdit('irc.freenode.org')

        layout.addWidget(self.serverName)

        layout.addWidget(QtGui.QLabel('Channel:'))

        self.channelName = QtGui.QLineEdit('#pangaea')

        layout.addWidget(self.channelName)

        layout.addWidget(QtGui.QLabel('Nick:'))

        self.nickName = QtGui.QLineEdit('ceruleanwave9832')

        layout.addWidget(self.nickName)

        self.connectButton = QtGui.QPushButton('Connect!')

        layout.addWidget(self.connectButton)

        self.connectButton.clicked.connect(self.connect_irc)

        self.view = QtGui.QListWidget()

        self.entry = QtGui.QLineEdit()

        self.entry.returnPressed.connect(self.send_message)

        irc_widget = QtGui.QWidget(self)

        vbox = QtGui.QVBoxLayout()

        vbox.addLayout(layout)

        vbox.addWidget(self.view)

        vbox.addWidget(self.entry)

        irc_widget.setLayout(vbox)

        self.setCentralWidget(irc_widget)

        self.setWindowTitle('IRC')

        self.setUnifiedTitleAndToolBarOnMac(True)

        self.showMaximized()

        self.protocol = None

    def connect_irc(self):
        self.connectButton.setDisabled(True)

        self.channelName.setDisabled(True)

        self.nickName.setDisabled(True)

        self.serverName.setDisabled(True)

        factory = IRCCoreFactory(self)

        server_name = self.serverName.text().encode('ascii')

        reactor.connectTCP(server_name, 6667, factory)

        # reactor.runReturn()
        # app.exit()
        #app.exit()

        reactor.run()

    def send_message(self):
        if self.protocol:
            chan_name = self.channelName.text().encode('ascii')

            message = self.entry.text().encode('ascii')

            self.protocol.msg(chan_name, message)

            self.view.addItem('%s <%s> %s' % (chan_name, self.protocol.nickname, message))
        else:
            self.view.addItem('Not connected.')
        self.entry.setText('')

    def closeEvent(self, event):
        print('Attempting to close the main window!')
        reactor.stop()
        event.accept()


if __name__ == '__main__':
    mainWin = MainWindow()
    sys.exit(app.exec_())
