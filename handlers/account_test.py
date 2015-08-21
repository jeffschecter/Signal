"""Tests for endpoints related to a user's account."""

import json
import logging
import unittest

import testutils

from storage import model


class AccountHandlerTest(unittest.TestCase):

  def testCreate(self):
    with testutils.TestApi() as api:
      users = [_ for _ in model.User.query()]
      self.assertEqual(0, len(users))
      resp = api(
        "/account/create", post=True,
        env={"latitude": 40.712784, "longitude": -74.005941},
        name="Johnny")
      self.assertEqual(resp['uid'], 0)


if __name__ == "__main__":
  unittest.main()
