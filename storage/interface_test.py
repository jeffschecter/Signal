"""Tests for the datastore interface."""

import datetime
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

  def testLoadAccount(self):
    user, match, search = interface.LoadAccount(1)
    self.assertTrue(user.key.id(), 1)
    with self.assertRaises(LookupError):
      interface.LoadAccount(12345)

  def testCreateAccount(self):
    now = datetime.datetime(2015, 1, 1)
    user, match, search = interface.CreateAccount("Foo", 15, 20, now)
    self.assertEqual("Foo", user.name)
    self.assertEqual(15, match.latitude)
    self.assertEqual(20, match.longitude)
    self.assertEqual(now, user.joined)
    self.assertEqual(now, match.last_activity)
    self.assertEqual(1, match.key.id())
    self.assertEqual(1, search.key.id())
    user2, match2, search2 = interface.LoadAccount(user.key.id())
    self.assertEqual(user, user2)
    self.assertEqual(match, match2)
    self.assertEqual(search, search2)

  def testUpdateAccount(self):
    u, _, _ = interface.CreateAccount("Foo", 0, 0, datetime.datetime.today())
    uid = u.key.id()
    with self.assertRaises(ValueError):
      interface.UpdateAccount(uid, joined=datetime.datetime.today())
    with self.assertRaises(ValueError):
      interface.UpdateAccount(uid, last_activity=datetime.datetime.today())
    with self.assertRaises(ValueError):
      interface.UpdateAccount(uid, latitud=10)
    with self.assertRaises(ValueError):
      interface.UpdateAccount(uid, longitude=10)
    with self.assertRaises(ValueError):
      interface.UpdateAccount(uid, foobarbaz=123)
    user, match, search = interface.UpdateAccount(
      uid,
      gender_string="genderqueer",
      gender=2,
      radius=100)
    self.assertEqual(user.gender_string, "genderqueer")
    self.assertEqual(match.gender, 2)
    self.assertEqual(search.radius, 100)
    user2, match2, search2 = interface.LoadAccount(uid)
    self.assertEqual(user2.gender_string, "genderqueer")
    self.assertEqual(match2.gender, 2)
    self.assertEqual(search2.radius, 100)

  def testPing(self):
    raise NotImplementedError()

  def testSetIntro(self):
    raise NotImplementedError()

  def testSetImage(self):
    raise NotImplementedError()


if __name__ == "__main__":
  unittest.main()
