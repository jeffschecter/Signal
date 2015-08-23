"""Utilities for testing the app."""

import datetime
import json
import webtest

import api

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


# --------------------------------------------------------------------------- #
# Setup helper that mocks out appengine infrastructure and simplifies         #
# calling endpoints.                                                          #
# --------------------------------------------------------------------------- #

class TestApi(object):

  def __init__(self, **default_env):
    self.default_env = default_env or DEFAULT_TEST_ENV
    self.Start()

  def Start(self):
    ndb.get_context().set_cache_policy(False)
    self.testbed = testbed.Testbed()
    self.testbed.activate()
    self.policy = datastore_stub_util.PseudoRandomHRConsistencyPolicy(
      probability=0)
    self.testbed.init_datastore_v3_stub(consistency_policy=self.policy)
    self.testbed.init_memcache_stub()
    self.test_app = webtest.TestApp(api.API)

  def Stop(self):
    self.testbed.deactivate()

  def Call(self, endpoint, post=False, expect_err=False, env=None, **kwargs):
    env = env or self.default_env
    method = self.test_app.post if post else self.test_app.get
    path = "{endpoint}?data={data}".format(
      endpoint=endpoint,
      data=json.dumps({"env": env, "args": kwargs}))
    resp = method(path)
    if resp.status_int != 200:
      raise RuntimeError(
        "Call to endpoint failed! {endpoint} {env} {args}".format(
          endpoint=endpoint, env=env, args=kwargs))
    else:
      resp = json.loads(resp.normal_body)
      env = resp['env']
      args = resp['args']
      if not expect_err:
        assert not env.get('error'), env['error_report']
      return env, args


# --------------------------------------------------------------------------- #
#  Provisioner that populates the stubbed out appengine resources.            #
# --------------------------------------------------------------------------- #

# These mappings are reasonable, not definitive.
SEX_MATH = {
  (0, 0): ([0, 2], [], []),                      # Gay male
  (0, 1): ([], [1, 2], []),                      # Straight male
  (0, 2): ([0, 2], [1, 2], []),                  # Bi male
  (0, 3): ([2, 3], [2, 3], [0, 1, 2, 3]),        # Queery male
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
  for gender in (0, 1, 2):
    for sexuality in (0, 1, 2, 3):
      for lat_offset in (-5, 0, 5):
        for long_offset in (-1, 0, 1):
          for age_offset in (-10, -5, 0, 5, 10):
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
