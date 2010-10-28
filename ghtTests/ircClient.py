from PySide.QtCore import *
from PySide.QtGui import *
import sys, qt4reactor

app = QApplication(sys.argv)
qt4reactor.install()

from twisted.words.protocols import irc
from twisted.internet import reactor, protocol
from twisted.python import log

import time, sys

class IRCCore(irc.IRCClient):
    nickname = 'dosdsdssd'
    def connectionMade(self):
        self.nickname = self.factory.nickname
        irc.IRCClient.connectionMade(self)
        self.log('connected!!')
    def connectionLost(self, reason):
        self.log('disconnected... :( %s'%reason)
    def signedOn(self):
        self.join(self.factory.channel)
    def joined(self, channel):
        self.log('joined %s'%channel)
    def privmsg(self, user, channel, msg):
        self.log('%s %s %s'%(user, channel, msg))
    def action(self, user, channel, msg):
        self.log('action: %s %s %s'%(user, channel, msg))
    def log(self, str):
        self.factory.view.addItem(str)

class IRCCoreFactory(protocol.ClientFactory):
    protocol = IRCCore
    def __init__(self, channel, nickname, view):
        self.channel = channel
        self.nickname = nickname
        self.view = view
    def clientConnectionLost(self, connector, reason):
        # reconnect to server if lose connection
        connector.connect()
    def clientConnectionFailed(self, connector, reason):
        print('connection failed! :(', reason)
        reactor.stop()

class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        connectLayout = QHBoxLayout()
        connectLayout.addWidget(QLabel('Server:'))
        self.serverName = QLineEdit('irc.freenode.org')
        connectLayout.addWidget(self.serverName)
        connectLayout.addWidget(QLabel('Channel:'))
        self.channelName = QLineEdit('#pangaea')
        connectLayout.addWidget(self.channelName)
        connectLayout.addWidget(QLabel('Nick:'))
        self.nickName = QLineEdit('ceruleanwave9832')
        connectLayout.addWidget(self.nickName)
        self.connectButton = QPushButton('Connect!')
        connectLayout.addWidget(self.connectButton)
        self.connectButton.clicked.connect(self.connectIRC)

        self.view = QListWidget()
        self.entry = QLineEdit()
        self.entry.returnPressed.connect(self.sendMessage)
        irc = QWidget(self)
        vbox = QVBoxLayout()
        vbox.addLayout(connectLayout)
        vbox.addWidget(self.view)
        vbox.addWidget(self.entry)
        irc.setLayout(vbox)
        self.setCentralWidget(irc)
        self.setWindowTitle('IRC')
        self.setUnifiedTitleAndToolBarOnMac(True)
        self.showMaximized()
    def connectIRC(self):
        self.connectButton.setDisabled(True)
        chanName = self.channelName.text().encode('ascii')
        nickName = self.nickName.text().encode('ascii')
        ircCoreFactory = IRCCoreFactory(chanName, nickName, self.view)
        serverName = self.serverName.text().encode('ascii')
        reactor.connectTCP(serverName, 6667, ircCoreFactory)
        #reactor.run()
    def sendMessage(self):
        print(self.entry.text())
    def closeEvent(self, event):
        print('Attempting to close the main window!')
        reactor.stop()
        event.accept()

if __name__ == '__main__':
    mainWin = MainWindow()
    reactor.runReturn()
    sys.exit(app.exec_())
