# pylint: disable=missing-docstring

"""Tests for the messaging endpoints."""

import base64
import datetime
import unittest

from google.appengine.ext import ndb
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
    audio = testutils.Resource("intro.aac")
    _, args = self.api.Call(
      "/message/send",
      recipient=2,
      blob=base64.b64encode(audio, "-_"))
    send_ts = args["send_timestamp_ms"]
    _, args = self.api.Call(
      "/message/listen",
      env={"uid": 2},
      sender=testutils.DEFAULT_UID,
      recipient=2,
      send_timestamp_ms=send_ts)
    blob_out = args["blob"]
    self.assertEqual(audio, blob)


  def testVerifyListen(self):
    pass