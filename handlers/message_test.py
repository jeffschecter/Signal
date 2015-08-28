# pylint: disable=missing-docstring

"""Tests for the messaging endpoints."""

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

  def testSendListen(self):
    blob_in = common.Encode(testutils.Resource("intro.aac"))
    _, args = self.api.Call(
        "/message/send",
        recipient=2,
        blob=blob_in)
    send_ts = args["send_timestamp_ms"]
    _, args = self.api.Call(
        "/message/listen",
        env={"uid": 2},
        sender=testutils.DEFAULT_UID,
        recipient=2,
        send_timestamp_ms=send_ts)
    blob_out = args["blob"]
    self.assertEqual(blob_in, blob_out)


  def testVerifyListen(self):
    env, _ = self.api.Call(
        "/message/listen",
        env={"uid": 3},
        expect_err=True,
        sender=1,
        recipient=2,
        send_timestamp_ms=12345)
    self.assertEqual(
        env["error_report"],
        ("VerificationError: While checking input: ValueError: "
         "User 3 tried to listen to a message from 1 to 2"))
