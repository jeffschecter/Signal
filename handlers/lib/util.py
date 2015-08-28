"""Utilities for defining endpoints."""

import common
import json
import logging
import webapp2

from google.appengine.ext import ndb
from handlers.lib import ioformat


# --------------------------------------------------------------------------- #
#  Some utilities.                                                            #
# --------------------------------------------------------------------------- #

class VerificationError(Exception):
  """Raised when endpoint inputs or outputs are invalid."""
  pass


def TODO():
  """Raises a NotImplementedError."""
  raise NotImplementedError("This endpoint has not been implemented.")


# --------------------------------------------------------------------------- #
#  Endpoint handler superclasses.                                             #
# --------------------------------------------------------------------------- #

class RequestHandler(webapp2.RequestHandler):
  """Generic request handler. Intended for subclassing."""

  # Subclasses should override in_format and out_format with subclasses of
  # ndb.Model. These models act as the canonical input and output formats.
  in_format = ndb.Expando
  out_format = ndb.Expando

  def __init__(self, *args, **kwargs):
    self.env = {}
    self.args = {}
    self.response_args = {}
    self.response_env = {}
    self.file = None
    webapp2.RequestHandler.__init__(self, *args, **kwargs)

  # pylint: disable=invalid-name
  def get(self):
    """Forward GET requests to the response processor."""
    self.Respond()

  # pylint: disable=invalid-name
  def post(self):
    """Forward POST requests to the response processor."""
    self.Respond()

  def SetArg(self, k, v):
    """Sets an otput argument.

    Args:
      k: (str) The name of the argument.
      v: (*) Its value. Must be JSON serializable.
    """
    self.response_args[k] = v

  def UpdateArgs(self, *models, **kwargs):
    """Set several output arguments at once.

    Args:
      models: (ndb.Model) Copy properties into the output arguments.
      kwargs: (dict) Multiple named arguments.
    """
    for model in models:
      d = model if isinstance(model, dict) else model.to_dict()
      for k, v in d.iteritems():
        if v not in ([], None):
          self.SetArg(k, v)
    self.response_args.update(kwargs)

  def GetArg(self, x):
    """Get the value of an input argument.

    Args:
      x: (str) The name of the argument to retrieve.

    Returns:
      (*) The argument's value, or None if absent.
    """
    return self.args.get(x)

  def SetEnv(self, k, v):
    """Set an output environmental variable.

    Args:
      k: (str) The name of the variable.
      v: (*) Its value. Must be JSON serializable.
    """
    self.response_env[k] = v

  def GetEnv(self, x):
    """Get the value of an input environmental variable.

    Args:
      x: (str) The name of the variable to retrieve.

    Returns:
      (*) The variable's value, or None if absent.
    """
    return self.env.get(x)

  # pylint: disable=protected-access
  def VerifyIn(self):
    """Validate the endpoint call."""
    try:
      self.in_format(**self.args)._check_initialized()
      self._VerifyIn()
    except Exception as e:
      raise VerificationError(
          "While checking input: {t}: {s}".format(
              t=type(e).__name__, s=str(e)))

  def _VerifyIn(self):
    """Subclasses should override with additional checks
    required to validate the request."""
    pass

  # pylint: disable=protected-access
  def VerifyOut(self):
    """Validate the response."""
    try:
      self.out_format(**self.response_args)._check_initialized()
      self._VerifyOut()
    except Exception as e:
      raise VerificationError(
          "While checking output: {t}: {s}".format(
              t=type(e).__name__, s=str(e)))

  def _VerifyOut(self):
    """Subclasses should override _VerifyOut to perform any additional checks
    required to validate the response."""
    pass

  def Output(self):
    """Serialize the response arguments and variables."""
    return json.dumps(
        {"env": self.response_env, "args": self.response_args},
        default=common.JsonEncoder)

  # pylint: disable=broad-except
  def Respond(self):
    """Process the request and write a response."""
    self.response.headers['Content-Type'] = 'text/json'
    try:
      query = json.loads(self.request.params.get('data'))
      self.env = query.get("env", {})
      self.args = query.get("args", {})
      self.VerifyIn()
      self.Handle()
      self.VerifyOut()
    except Exception as e:
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
  """Accepts requests for endpoints that require a user to be logged in."""

  def _VerifyIn(self):
    """Check whether we have a real signed-in user."""
    #TODO Actually authenticate
    if not self.GetEnv("uid"):
      raise VerificationError("Auth failed: {env}".format(env=self.env))


class FileAcceptingAuthedHandler(AuthedHandler):
  """Accepts short files encoded as url-safe base64 strings, with the "-"
  and "_" characters used in place of "+" and "/". The file should be placed
  in the "blob" argument of the request json."""

  in_format = ioformat.Blob
  out_format = ioformat.Trivial

  def _VerifyIn(self):
    """Check that the caller sent a file."""
    AuthedHandler._VerifyIn(self)
    self.file = common.Decode(self.GetArg("blob"))
