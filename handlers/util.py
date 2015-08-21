"""Utilities for defining endpoints."""

import json
import logging
import webapp2


class VerificationError(Exception):
  pass


def JsonEncoder(obj):
  # For date, time, and datetime, convert to isoformat string
  if hasattr(obj, 'isoformat'):
    return obj.isoformat()
  else:
    raise TypeError(
      "Object of type {ty} with value of {val} is not JSON serializable".format(
        ty=type(obj),
        val=repr(obj)))


class RequestHandler(webapp2.RequestHandler):

  def __init__(self, *args, **kwargs):
    webapp2.RequestHandler.__init__(self, *args, **kwargs)

  def get(self):
    self.Respond()

  def post(self):
    self.Respond()

  def Set(self, k, v):
    self.response_data[k] = v

  def Arg(self, x):
    return self.args.get(x)

  def Env(self, x):
    return self.env.get(x)

  def Verify(self):
    """Subclasses should overwrite this method to check expectations and raise
    an VerificationError when requirements are not satisfied."""
    pass

  def Respond(self):
    self.response.headers['Content-Type'] = 'text/json'
    self.response_data = {}
    try:
      query = json.loads(self.request.params.get('data'))
      self.env = query.get("env", {})
      self.args = query.get("args", {})
      self.Verify()
      self.Handle()
      response_str = json.dumps(self.response_data, default=JsonEncoder)
    except Exception as e:
      logging.exception(e)
      response_str = json.dumps({
        "error": type(e).__name__,
        "error_string": str(e)})
    finally:
      self.response.write(response_str)


class AuthedHandler(RequestHandler):

  def __init__(self, *args, **kwargs):
    AuthedHandler.__init__(self, *args, **kwargs)

  def Verify(self):
    #TODO Actually authenticate
    if not self.Env("uid"):
      raise AuthenticationError("Auth failed: {env}".format(env=self.env))


def TODO():
  raise NotImplementedError("This endpoint has not been implemented.")
