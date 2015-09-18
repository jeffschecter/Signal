# pylint: disable=missing-docstring

"""Tests for the history endpoints."""

import common
import datetime
import unittest

from google.appengine.ext import ndb
from handlers.lib import util
from storage import interface
from storage import model
from test import testutils


class HistoryTest(unittest.TestCase):

  @classmethod
  def setUpClass(cls):
    cls.api = testutils.TestApi()
    testutils.FakeUsers(5)

  @classmethod
  def tearDownClass(cls):
    cls.api.Stop()

  def testLoad(self):
    _, args = self.api.Call("/history/load")


if __name__ == "__main__":
  unittest.main()
