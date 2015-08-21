"""Tests for handlers.account endpoints."""

import json
import logging
import unittest

import testutils

from storage import interface
from storage import model


class AccountHandlerTest(unittest.TestCase):

  @classmethod
  def setUpClass(cls):
    cls.api = testutils.TestApi()
    testutils.FakeUsers(1)

  @classmethod
  def tearDownClass(cls):
    cls.api.Stop()

  def testCreate(self):
    env, args = self.api.Call(
      "/account/create",
      env={"latitude": testutils.DEFAULT_TEST_ENV["latitude"],
           "longitude": testutils.DEFAULT_TEST_ENV["longitude"]},
      name="Johnny")
    uid = args["uid"]
    user, match, search = interface.LoadAccount(uid)
    self.assertEqual(user.name, "Johnny")
    self.assertEqual(match.latitude, testutils.DEFAULT_LATITUDE)
    self.assertEqual(match.longitude, testutils.DEFAULT_LONGITUDE)

  def testLoad(self):
    env, args = self.api.Call("/account/load", uid=1)
    self.assertEqual(args["uid"], 1)

  def testSetIntro(self):
    env, args = self.api.Call("/account/set_intro", blob="")

  def testSetImage(self):
    env, args = self.api.Call("/account/set_image", blob="")

  def testBio(self):
    env, args = self.api.Call("/account/bio", gender=0, sexuality=1)
    env, args = self.api.Call(
      "/account/bio",
      gender=2, gender_string="genderqueer",
      sexuality=3, sexuality_string="queer")

  def testPreferences(self):
    env, args = self.api.Call(
      "/account/preferences",
      radius=testutils.DEFAULT_RADIUS * 2,
      min_age=testutils.DEFAULT_AGE + 5,
      max_age=testutils.DEFAULT_AGE + 10,
      accept_male_sexualities=[0, 1, 2, 3],
      accept_female_sexualities=[],
      accept_other_sexualities=[])

  def testDeactivate(self):
    env, args = self.api.Call("/account/deactivate")
    self.assertTrue(args.get("timestamp"))

  def testReactivate(self):
    env, args = self.api.Call("/account/reactivate")
    self.assertTrue(args.get("timestamp"))

  def testLogout(self):
    env, args = self.api.Call("/account/logout")

  def testPing(self):
    env, args = self.api.Call("account/ping")
    self.asertEqual(
      set(args.keys()),
      set(["latitude", "longitude", "country", "region", "city"]))


if __name__ == "__main__":
  unittest.main()
