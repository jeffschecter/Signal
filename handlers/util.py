"""Utilities for defining endpoints."""

import json
import logging
import webapp2


# --------------------------------------------------------------------------- #
#  Some utilities.                                                            #
# --------------------------------------------------------------------------- #

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


def TODO():
  raise NotImplementedError("This endpoint has not been implemented.")


# --------------------------------------------------------------------------- #
#  Endpoint handler templates.                                                #
# --------------------------------------------------------------------------- #

class RequestHandler(webapp2.RequestHandler):

  def __init__(self, *args, **kwargs):
    webapp2.RequestHandler.__init__(self, *args, **kwargs)

  def get(self):
    self.Respond()

  def post(self):
    self.Respond()

  def SetArg(self, k, v):
    self.response_args[k] = v

  def UpdateArgs(self, d={}, **kwargs):
    self.response_args.update(d)
    self.response_args.update(kwargs)

  def SetEnv(self, k, v):
    self.response_env[k] = v

  def Arg(self, x):
    return self.args.get(x)

  def Env(self, x):
    return self.env.get(x)

  def Verify(self):
    """Subclasses should overwrite this method to check expectations and raise
    an VerificationError when requirements are not satisfied."""
    pass

  def Output(self, **kwargs):
    return json.dumps(
      {"env": self.response_env, "args": kwargs or self.response_args},
      default=JsonEncoder)

  def Respond(self):
    self.response.headers['Content-Type'] = 'text/json'
    self.response_args = {}
    self.response_env = {}
    try:
      query = json.loads(self.request.params.get('data'))
      self.env = query.get("env", {})
      self.args = query.get("args", {})
      self.Verify()
      self.Handle()
    except Exception as e:
      logging.exception(e)
      self.SetEnv("error", True)
      self.SetEnv("error_type", type(e).__name__)
      self.SetEnv("error_string", str(e))
    finally:
      self.response.write(self.Output())


class AuthedHandler(RequestHandler):

  def __init__(self, *args, **kwargs):
    RequestHandler.__init__(self, *args, **kwargs)

  def Verify(self):
    #TODO Actually authenticate
    if not self.Env("uid"):
      raise AuthenticationError("Auth failed: {env}".format(env=self.env))
