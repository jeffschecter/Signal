# pylint: disable=missing-docstring

"""Tests for the gardening endpoints."""

import common
import datetime
import unittest

from google.appengine.ext import ndb
from handlers.lib import util
from storage import interface
from storage import model
from test import testutils


class InterfaceTest(unittest.TestCase):

  @classmethod
  def setUpClass(cls):
    cls.api = testutils.TestApi()
    testutils.FakeUsers(3)

  @classmethod
  def tearDownClass(cls):
    cls.api.Stop()

  def testLoad(self):
    #TODO
    pass

  def testSend(self):
    #TODO
    pass

  def testWater(self):
    #TODO
    pass


if __name__ == "__main__":
  unittest.main()
