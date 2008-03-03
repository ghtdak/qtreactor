import sys

import sys

from twisted.application import reactors
reactors.installReactor('qt4')

from twisted.internet import reactor, task
from twisted.python import log
log.startLogging(sys.stdout)
 
class doNothing(object):
    def __init__(self):
        self.count = 0
        self.looping=false
        
    def doSomething(self):
        self.count += 1
        reactor.callLater(0.05,self.doSomething)
        
    def printStat(self):
        log.msg(' c = : ' + str(self.count) + ' r = : ' + str(reactor.simCount))
        
t=doNothing()

task.LoopingCall(t.printStat).start(5.0)
reactor.callLater(5000.0,reactor.stop)
    
reactor.callWhenRunning(t.doSomething)
log.msg('calling reactor.run()')
reactor.run()
log.msg('fell off the bottom?...')

