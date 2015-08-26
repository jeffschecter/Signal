"""Utilities for defining endpoints."""

import base64
import json
import logging
import webapp2

from google.appengine.ext import ndb
from handlers.lib import ioformat


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
      "Object of type {t} with value of {v} is not JSON serializable".format(
        t=type(obj),
        v=repr(obj)))


def TODO():
  raise NotImplementedError("This endpoint has not been implemented.")


# --------------------------------------------------------------------------- #
#  Endpoint handler superclasses.                                             #
# --------------------------------------------------------------------------- #

class RequestHandler(webapp2.RequestHandler):

  # Subclasses should override in_format and out_format with subclasses of
  # ndb.Model. These models act as the canonical input and output formats.
  in_format = ndb.Expando
  out_format = ndb.Expando

  def get(self):
    self.Respond()

  def post(self):
    self.Respond()

  def SetArg(self, k, v):
    self.response_args[k] = v

  def UpdateArgs(self, *models, **kwargs):
    for model in models:
      d = model if type(model) == dict else model.to_dict()
      for k, v in d.iteritems():
        if v not in ([], None):
          self.SetArg(k, v)
    self.response_args.update(kwargs)

  def GetArg(self, x):
    return self.args.get(x)

  def SetEnv(self, k, v):
    self.response_env[k] = v

  def GetEnv(self, x):
    return self.env.get(x)

  def VerifyIn(self):
    try:
      self.in_format(**self.args)._check_initialized()
      self._VerifyIn()
    except Exception as e:
      raise VerificationError(
        "While checking input: {t}: {s}".format(t=type(e).__name__, s=str(e)))

  def _VerifyIn(self):
    """Subclasses should override _VerifyIn to perform any additional checks
    required to validate the request."""
    pass

  def VerifyOut(self):
    try:
      self.out_format(**self.response_args)._check_initialized()
      self._VerifyOut()
    except Exception as e:
      raise VerificationError(
        "While checking output: {t}: {s}".format(t=type(e).__name__, s=str(e)))

  def _VerifyOut(self):
    """Subclasses should override _VerifyOut to perform any additional checks
    required to validate the response."""
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
      self.VerifyIn()
      self.Handle()
      self.VerifyOut()
    except Exception as e:
      if not self.__dict__.get("env"):
        import pdb; pdb.set_trace()
      logging.exception(e)
      self.SetEnv("error", True)
      if self.GetEnv("debug"):
        self.SetEnv(
          "error_report", "{t}: {s}".format(t=type(e).__name__, s=str(e)))
      else:
        self.SetEnv("error_report", "Something went wrong.")
    finally:
      self.response.write(self.Output())


class AuthedHandler(RequestHandler):

  def _VerifyIn(self):
    #TODO Actually authenticate
    if not self.GetEnv("uid"):
      raise AuthenticationError("Auth failed: {env}".format(env=self.env))


class FileAcceptingAuthedHandler(AuthedHandler):

  in_format = ioformat.Blob
  out_format = ioformat.Trivial

  def decode(self, b64):
    missing_padding = 4 - len(b64) % 4
    if missing_padding:
        b64 += b'='* missing_padding
    return base64.b64decode(str(b64), "-_")

  def _VerifyIn(self):
    AuthedHandler._VerifyIn(self)
    self.file = self.decode(self.GetArg("blob"))
