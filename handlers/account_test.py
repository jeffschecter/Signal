"""Tests for handlers.account endpoints."""

import base64
import unittest

from storage import interface
from storage import model
from test import testutils


class AccountHandlerTest(unittest.TestCase):

  @classmethod
  def setUpClass(cls):
    cls.api = testutils.TestApi()
    testutils.FakeUsers(1)

  @classmethod
  def tearDownClass(cls):
    cls.api.Stop()

  def testCreate(self):
    _, args = self.api.Call(
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
    _, args = self.api.Call("/account/load")
    self.assertEqual(args["uid"], testutils.DEFAULT_UID)

  def testSetIntro(self):
    audio = testutils.Resource("intro.aac")
    self.api.Call("/account/set_intro", blob=base64.b64encode(audio, "-_"))
    out_audio = interface.GetForUid(model.IntroFile, testutils.DEFAULT_UID).blob
    self.assertEqual(audio, out_audio)

  def testSetImage(self):
    img = testutils.Resource("icon.png")
    self.api.Call("/account/set_image", blob=base64.b64encode(img, "-_"))
    out_img = interface.GetForUid(model.ImageFile, testutils.DEFAULT_UID).blob
    self.assertEqual(img, out_img)

  def testBio(self):
    env, _ = self.api.Call(
      "/account/bio", expect_err=True, gender=0, gender_string="genderqueer")
    self.assertEqual(
      env["error_report"],
      ("VerificationError: While checking input: ValueError: "
       "Only set a gender string if gender == 2."))
    env, _ = self.api.Call(
      "/account/bio", expect_err=True, sexuality=0, sexuality_string="queer")
    self.assertEqual(
      env["error_report"],
      ("VerificationError: While checking input: ValueError: "
       "Only set a sexuality string if sexuality == 3."))
    env, _ = self.api.Call("/account/bio", expect_err=True)
    self.assertEqual(
      env["error_report"],
      ("VerificationError: While checking input: ValueError: "
       "Must specify gender or sexuality."))
    self.api.Call("/account/bio", gender=0, sexuality=1)
    self.api.Call("/account/bio", gender=0)
    self.api.Call("/account/bio", sexuality=1)
    self.api.Call(
      "/account/bio",
      gender=2, gender_string="genderqueer",
      sexuality=3, sexuality_string="queer")
    user, match, _ = interface.LoadAccount(testutils.DEFAULT_UID)
    self.assertEqual(user.gender_string, "genderqueer")
    self.assertEqual(user.sexuality_string, "queer")
    self.assertEqual(match.gender, 2)
    self.assertEqual(match.sexuality, 3)

  def testPreferences(self):
    self.api.Call(
      "/account/preferences",
      radius=testutils.DEFAULT_RADIUS * 2,
      min_age=testutils.DEFAULT_AGE + 5,
      max_age=testutils.DEFAULT_AGE + 10,
      accept_male_sexualities=[0, 1, 2, 3],
      accept_female_sexualities=[],
      accept_other_sexualities=[])
    _, _, search = interface.LoadAccount(testutils.DEFAULT_UID)
    self.assertEqual(search.radius, testutils.DEFAULT_RADIUS * 2)
    self.assertEqual(search.min_age, testutils.DEFAULT_AGE + 5)
    self.assertEqual(search.max_age, testutils.DEFAULT_AGE + 10)
    self.assertEqual(set(search.accept_male_sexualities), set([0, 1, 2, 3]))
    self.assertEqual(set(search.accept_female_sexualities), set())
    self.assertEqual(set(search.accept_other_sexualities), set())

  def testDeactivateReactivate(self):
    _, match, _ = interface.LoadAccount(testutils.DEFAULT_UID)
    self.assertEqual(match.active, True)
    env, args = self.api.Call("/account/deactivate")
    _, match, _ = interface.LoadAccount(testutils.DEFAULT_UID)
    self.assertEqual(match.active, False)
    env, args = self.api.Call("/account/reactivate")
    _, match, _ = interface.LoadAccount(testutils.DEFAULT_UID)
    self.assertEqual(match.active, True)

  def testLogout(self):
    self.api.Call("/account/logout")

  def testPing(self):
    self.api.Call("/account/ping")
    env, _ = self.api.Call(
      "/account/ping", expect_err=True, env={"latitude": 200})
    self.assertEqual(
      env["error_report"],
      ("AssertionError: "
       "Latitude and Longitude must be between -180 and 180."))


if __name__ == "__main__":
  unittest.main()
