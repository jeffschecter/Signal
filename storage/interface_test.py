"""Tests for the datastore interface."""

import unittest
import testutils

from google.appengine.ext import ndb
from storage import interface
from storage import model


class UtilitiesTest(unittest.TestCase):

  @classmethod
  def setUpClass(cls):
    cls.api = testutils.TestApi()
    testutils.FakeUsers(1)

  @classmethod
  def tearDownClass(cls):
    cls.api.Stop()

  def testGuarantee(self):
    return
    with self.assertRaises(LookupError):
      interface.Guarantee(None)
    with self.assertRaises(LookupError):
      interface.Guarantee(model.User.get_by_id(12345))
    self.assertTrue(model.User.get_by_id(1))

  def testUKey(self):
    self.assertEqual(interface.UKey(1), model.User(id=1).key)

  def testGetUser(self):
    self.assertEqual(interface.GetUser(1).key.id(), 1)
    with self.assertRaises(LookupError):
      interface.GetUser(12345)

  def testGetForUid(self):
    self.assertEqual(
      interface.GetForUid(model.MatchParameters, 1),
      model.MatchParameters.get_by_id(1, parent=ndb.Key(model.User, 1)))
    with self.assertRaises(LookupError):
      interface.GetForUid(model.MatchParameters, 12345)


if __name__ == "__main__":
  unittest.main()
