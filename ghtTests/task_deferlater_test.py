from __future__ import print_function
__author__ = 'ght'

from twisted.application import reactors

reactors.installReactor('qt4')

from twisted.trial import unittest
from twisted.internet import reactor, task


class TrialTest1(unittest.TestCase):

    def setUp(self):
        print("setUp()")

    def test_main(self):
        print("test_main")
        return task.deferLater(reactor, 1, self._called_by_deffered1)

    def _called_by_deffered1(self):
        print("_called_by_deffered1")
        return task.deferLater(reactor, 1, self._called_by_deffered2)

    def _called_by_deffered2(self):
        print("_called_by_deffered2")

    def tearDown(self):
        print("tearDown()")

