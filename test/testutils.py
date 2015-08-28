"""Utilities for testing the app."""

import api
import datetime
import json
import logging
import os
import webtest

from google.appengine.datastore import datastore_stub_util
from google.appengine.ext import ndb
from google.appengine.ext import testbed
from storage import interface


DEFAULT_UID = 1
DEFAULT_LATITUDE = 40.712784
DEFAULT_LONGITUDE = -74.005941
DEFAULT_AGE = 30
DEFAULT_RADIUS = 5


DEFAULT_TEST_ENV = {
  "debug": True,
  "uid": DEFAULT_UID,
  "latitude": DEFAULT_LATITUDE,
  "longitude": DEFAULT_LONGITUDE}


def Resource(handle):
  fname = os.path.join(os.path.dirname(__file__), "resources", handle)
  with open(fname, "r") as f:
    return f.read()


# --------------------------------------------------------------------------- #
# Setup helper that mocks out appengine infrastructure and simplifies         #
# calling endpoints.                                                          #
# --------------------------------------------------------------------------- #

class TestApi(object):

  def __init__(self, **default_env):
    self.default_env = DEFAULT_TEST_ENV
    self.default_env.update(default_env)
    self.Start()

  def Start(self):
    self.testbed = testbed.Testbed()
    self.testbed.activate()
    self.policy = datastore_stub_util.PseudoRandomHRConsistencyPolicy(
      probability=0)
    self.testbed.init_datastore_v3_stub(consistency_policy=self.policy)
    self.testbed.init_memcache_stub()
    ndb.get_context().clear_cache()
    self.test_app = webtest.TestApp(api.API)

  def Stop(self):
    self.testbed.deactivate()
    del(self.test_app.app)

  def Call(self, endpoint, post=False, expect_err=False, env=None, **kwargs):
    """Mocks a call to the server.

    Args:
      endpoint: (str) The route of the target endpoint.
      post: (boolean) True for a POST request, defaults to GET.
      expect_err: (boolean) Unless true, raise an error if the response
        environment has the 'error' or 'error_report' fields set.
      env: (dict) Overrides to the default request environment.
      kwargs: (dict) Request args.

    Returns:
      (dict, dict) The response environment and arguments.
    """
    req_env = dict(self.default_env)
    if env:
      req_env.update(env)
    method = self.test_app.post if post else self.test_app.get
    path = "{endpoint}?data={data}".format(
      endpoint=endpoint,
      data=json.dumps({"env": req_env, "args": kwargs}))
    resp = json.loads(method(path).normal_body)
    resp_env = resp.get('env')
    resp_args = resp.get('args')
    if not expect_err:
      assert not resp_env.get('error'), resp_env.get('error_report')
    return resp_env, resp_args


# --------------------------------------------------------------------------- #
#  Populate the stubbed out appengine data store with fake users.             #
# --------------------------------------------------------------------------- #

# These mappings are reasonable, not definitive.
SEX_MATH = {
  (0, 0): ([0, 2], [], []),                      # Gay male
  (0, 1): ([], [1, 2], []),                      # Straight male
  (0, 2): ([0, 2], [1, 2], []),                  # Bi male
  (0, 3): ([2, 3], [2, 3], [0, 1, 2, 3]),        # Queer male
  (1, 0): ([], [0, 2], []),                      # Gay female
  (1, 1): ([1, 2], [], []),                      # Straight female
  (1, 2): ([1, 2], [0, 2], []),                  # Bi female
  (1, 3): ([2, 3], [2, 3], [0, 1, 2, 3]),        # Queer female
  (2, 0): ([0, 2, 3], [0, 2, 3], []),            # Gay genderqueer
  (2, 1): ([1, 2, 3], [1, 2, 3], []),            # Straight genderqueer
  (2, 2): ([0, 2, 3], [0, 2, 3], []),            # Bi genderqueer
  (2, 3): ([0, 2, 3], [0, 2, 3], [0, 1, 2, 3])}  # Queer genderqueer


def FakeUsers(cap=None):
  uid = 0
  now = datetime.datetime.today()
  for age_offset in (0, -10, -5, 5, 10):
    for long_offset in (0, -5, 5):
      for lat_offset in (0, -5, 5):
        for sexuality in (0, 1, 2, 3):
          for gender in (0, 1, 2):
            uid += 1
            if cap and uid > cap:
              break
            name = "User_{uid}".format(uid=uid)
            latitude = DEFAULT_LATITUDE + lat_offset
            longitude = DEFAULT_LONGITUDE + long_offset
            age = DEFAULT_AGE + age_offset
            ams, afs, aos = SEX_MATH[(gender, sexuality)]

            # Create the user
            interface.CreateAccount(name, latitude, longitude)
            interface.UpdateAccount(
              uid,
              gender_string="genderqueer" if gender == 2 else None,
              sexuality_string="queer" if sexuality == 3 else None,
              gender=gender,
              sexuality=sexuality,
              birthday=now - datetime.timedelta(days=age * 365),
              radius=DEFAULT_RADIUS,
              min_age=int((age / 2) + 7),
              max_age=int(2 * (age - 7)),
              accept_male_sexualities=ams,
              accept_female_sexualities=afs,
              accept_other_sexualities=aos)
