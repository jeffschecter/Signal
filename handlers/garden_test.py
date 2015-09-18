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


class GardenTest(unittest.TestCase):

  @classmethod
  def setUpClass(cls):
    cls.api = testutils.TestApi()
    testutils.FakeUsers(2)

  @classmethod
  def tearDownClass(cls):
    cls.api.Stop()

  def testLoad(self):
    _, args = self.api.Call("/garden/load")
    r1, r2, r3 = args["roses"]
    self.assertEqual(1, r1["id"])
    self.assertEqual(2, r2["id"])
    self.assertEqual(3, r3["id"])

  def testSend(self):
    _, args = self.api.Call("/garden/send", recipient=2, rose_number=1)
    self.assertTrue(args["success"])
    _, args = self.api.Call("/garden/send", recipient=2, rose_number=1)
    self.assertFalse(args["success"])

  def testWaterPayment(self):
    #TODO
    pass

  def testWaterInvite(self):
    #TODO
    pass

  def testWaterLotto(self):
    #TODO
    pass


if __name__ == "__main__":
  unittest.main()
