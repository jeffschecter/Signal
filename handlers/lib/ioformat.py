"""Endpoint input formats."""

from google.appengine.ext import ndb


class BlobProperty(ndb.BlobProperty):
  """Wrapper that performs some additional validation.

  Datastore treats ASCII text strings as interchangeable with binary blobs, but
  not so for unicode strings. The webapp2 framework treats all incoming requests
  as unicode, se we need to cerce blobs to ASCII strings before storing them.
  """

  # pylint: disable=no-self-use
  def _validate(self, value):
    """Coerves unicode blobs to strings."""
    return str(value)


class Trivial(ndb.Model):
  """No arguments."""
  pass


class Blob(ndb.Model):
  """Nothing but a raw (or encoded) file blob."""
  blob = BlobProperty(required=True)


class DesignateUser(ndb.Model):
  """Nothing but a "partner" user for the logged-in user to interact with."""
  uid = ndb.IntegerProperty(required=True)
