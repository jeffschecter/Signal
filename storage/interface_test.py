# pylint: disable=missing-docstring

"""Tests for the datastore interface."""

import datetime
import unittest

from google.appengine.ext import ndb
from storage import interface
from storage import model
from test import testutils


class InterfaceUtilsTest(unittest.TestCase):

  @classmethod
  def setUpClass(cls):
    cls.api = testutils.TestApi()
    testutils.FakeUsers(2)

  @classmethod
  def tearDownClass(cls):
    cls.api.Stop()

  def testGuarantee(self):
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

  def testRelationshipRelationships(self):
    rel_12 = interface.Relationship(1, 2)
    rel_21 = interface.Relationship(2, 1)
    rels_12 = interface.Relationships(1, 2)
    rels_21 = interface.Relationships(2, 1)
    self.assertEqual(rel_12, rels_12[0], rels_21[1])
    self.assertEqual(rel_21, rels_12[1], rels_21[0])
    self.assertFalse(rel_12 == rel_21)
    rel_12 = interface.Relationship(1, 2, full=True)
    rel_21 = interface.Relationship(2, 1, full=True)
    rels_12 = interface.Relationships(1, 2, full=True)
    rels_21 = interface.Relationships(2, 1, full=True)
    self.assertEqual(rel_12, rels_12[0], rels_21[1])
    self.assertEqual(rel_21, rels_12[1], rels_21[0])
    self.assertFalse(rel_12 == rel_21)
    with self.assertRaises(ValueError):
      interface.Relationship(1, 1)

  def testGetForRelationship(self):
    rel_key = model.Relationship(id=2, parent=interface.UKey(1)).key
    model.MessageFile(id=123, parent=rel_key, blob="abc123").put()
    blob = interface.GetForRelationship(model.MessageFile, 1, 2, 123).blob
    self.assertEqual(blob, "abc123")


class InterfaceAccountTest(unittest.TestCase):

  @classmethod
  def setUpClass(cls):
    cls.api = testutils.TestApi()
    testutils.FakeUsers(2)

  @classmethod
  def tearDownClass(cls):
    cls.api.Stop()

  def testLoadAccount(self):
    user, _, _ = interface.LoadAccount(1)
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
    interface.GetGrowingRose(1, 1)
    interface.GetGrowingRose(1, 2)
    interface.GetGrowingRose(1, 3)
    user2, match2, search2 = interface.LoadAccount(user.key.id())
    self.assertEqual(user, user2)
    self.assertEqual(match, match2)
    self.assertEqual(search, search2)

  def testUpdateAccount(self):
    user, _, _ = interface.CreateAccount("Foo", 0, 0, datetime.datetime.today())
    uid = user.key.id()
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
    start = datetime.datetime.today()
    match = interface.Ping(1, 100, 150)
    stop = datetime.datetime.today()
    self.assertEqual(100, match.latitude)
    self.assertEqual(150, match.longitude)
    self.assertTrue(
        start <= match.last_activity and match.last_activity <= stop)
    _, match2, _ = interface.LoadAccount(1)
    self.assertEqual(100, match2.latitude)
    self.assertEqual(150, match2.longitude)
    self.assertTrue(
        start <= match2.last_activity and match2.last_activity <= stop)

  def testGetSetIntro(self):
    in_blob = testutils.Resource("intro.aac")
    interface.SetIntro(1, in_blob)
    out_blob = interface.GetIntro(1)
    self.assertEqual(in_blob, out_blob)
    with self.assertRaises(ValueError):
      interface.SetIntro(1, testutils.Resource("intro_toolong.aac"))
    with self.assertRaises(ValueError):
      interface.SetIntro(1, testutils.Resource("icon.png"))

  def testGetSetImage(self):
    in_blob = testutils.Resource("icon.png")
    interface.SetImage(1, in_blob)
    out_blob = interface.GetImage(1)
    self.assertEqual(in_blob, out_blob)
    with self.assertRaises(ValueError):
      interface.SetImage(1, testutils.Resource("icon_toobig.png"))
    with self.assertRaises(ValueError):
      interface.SetImage(1, testutils.Resource("intro.aac"))


class InterfaceMessageTest(unittest.TestCase):

  @classmethod
  def setUpClass(cls):
    cls.api = testutils.TestApi()
    testutils.FakeUsers(2)

  @classmethod
  def tearDownClass(cls):
    cls.api.Stop()

  def testCanMessage(self):
    #TODO
    pass

  def testSendMessageAndGetMessageFile(self):
    now = datetime.datetime.today()
    in_blob = testutils.Resource("intro.aac")
    interface.SendMessage(1, 2, in_blob, now=now)

    # Retrieve without marking the message as listened to
    out_blob = interface.GetMessageFile(1, 2, now, False)
    self.assertEqual(in_blob, out_blob)
    sender_rel = interface.Relationship(1, 2)
    recip_rel = interface.Relationship(2, 1)
    sent_msg = interface.GetForRelationship(
        model.SentMessage, 1, 2, now)
    rcvd_msg = interface.GetForRelationship(
        model.ReceivedMessage, 2, 1, now)
    self.assertEqual(now, sender_rel.last_sent_message)
    self.assertEqual(now, recip_rel.last_received_message)
    self.assertEqual(1, recip_rel.new_messages)
    self.assertEqual(True, sent_msg.new)
    self.assertEqual(True, rcvd_msg.new)
    self.assertEqual([], sent_msg.retrieved)
    self.assertEqual([], rcvd_msg.retrieved)

    # Retrieve again, this time marking it as listened
    now2 = now + datetime.timedelta(days=1)
    interface.GetMessageFile(1, 2, now, True, now=now2)
    recip_rel = interface.Relationship(2, 1)
    sent_msg = interface.GetForRelationship(
        model.SentMessage, 1, 2, now)
    rcvd_msg = interface.GetForRelationship(
        model.ReceivedMessage, 2, 1, now)
    self.assertEqual(0, recip_rel.new_messages)
    self.assertEqual(False, sent_msg.new)
    self.assertEqual(False, rcvd_msg.new)
    self.assertEqual([now2], sent_msg.retrieved)
    self.assertEqual([now2], rcvd_msg.retrieved)

    # Retrieve and mark as listened once more, ensure retrievals count up and
    # affect on number of new messages is idempotent
    now3 = now + datetime.timedelta(days=2)
    interface.GetMessageFile(1, 2, now, True, now=now3)
    recip_rel = interface.Relationship(2, 1)
    sent_msg = interface.GetForRelationship(
        model.SentMessage, 1, 2, now)
    rcvd_msg = interface.GetForRelationship(
        model.ReceivedMessage, 2, 1, now)
    self.assertEqual(0, recip_rel.new_messages)
    self.assertEqual(False, sent_msg.new)
    self.assertEqual(False, rcvd_msg.new)
    self.assertEqual([now2, now3], sent_msg.retrieved)
    self.assertEqual([now2, now3], rcvd_msg.retrieved)


class InterfaceGardenTest(unittest.TestCase):

  @classmethod
  def setUpClass(cls):
    cls.api = testutils.TestApi()
    testutils.FakeUsers(2)

  @classmethod
  def tearDownClass(cls):
    cls.api.Stop()

  def testRandomGrowingPeriod(self):
    # This one's probabilistic
    periods = [interface.RandomGrowingPeriod() for _ in xrange(10000)]
    mean = (sum(periods, datetime.timedelta(hours=0)) /
            len(periods)).total_seconds() / (60 * 60)  # hours
    self.assertTrue(mean > 23)
    self.assertTrue(mean < 25)

  def testGetGrowingRose(self):
    with self.assertRaises(AssertionError):
      interface.GetGrowingRose(1, 0)
    interface.GetGrowingRose(1, 1)
    interface.GetGrowingRose(1, 2)
    interface.GetGrowingRose(1, 3)
    with self.assertRaises(AssertionError):
      interface.GetGrowingRose(1, 4)

  def testGetGarden(self):
    garden = interface.GetGarden(1)
    self.assertEqual(3, len(garden))
    self.assertEqual([1, 2, 3], [rose.key.id() for rose in garden])
    with self.assertRaises(LookupError):
      interface.GetGarden(12345)

  def testSendRose(self):
    now = interface.SendRose(1, 2, 1)
    interface.GetForRelationship(model.SentRose, 1, 2, now)
    interface.GetForRelationship(model.ReceivedRose, 2, 1, now)
    newly_planted_rose = interface.GetGrowingRose(1, 1)
    self.assertTrue(
        (newly_planted_rose.bloomed - now) >= datetime.timedelta(hours=1))
    send_again = interface.SendRose(1, 2, 1)
    self.assertEqual(None, send_again)

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
