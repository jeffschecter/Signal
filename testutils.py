"""Utilities for testing the app."""

import json
import unittest
import webtest

import api

from google.appengine.ext import ndb
from google.appengine.ext import testbed


class TestApi(object):

  def __init__(self, provisioners=[], default_env=None):
    self.provisioners = provisioners
    self.default_env = default_env or {
      "uid": 123,
      "latitude": 40.712784,
      "longitude": -74.005941}

  def __enter__(self):
    ndb.get_context().set_cache_policy(False)
    self.testbed = testbed.Testbed()
    self.testbed.activate()
    self.testbed.init_datastore_v3_stub()
    for provisioner in self.provisioners:
      provisioner()
    self.test_app = webtest.TestApp(api.API)
    return self.HitEndpoint

  def __exit__(self):
    self.testbed.deactivate()

  def HitEndpoint(self, endpoint, post=False, env=None, **kwargs):
    env = env or self.default_env
    method = self.test_app.post if post else self.test_app.get
    path = "{endpoint}?data={data}".format(
      endpoint=endpoint,
      data=json.dumps({"env": env, "args": kwargs}))
    return method(path)
