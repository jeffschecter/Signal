"""Endpoint input formats."""

from google.appengine.ext import ndb


class BlobProperty(ndb.BlobProperty):
  """Wrapper that performs some additional validation.

  Datastore treats ASCII text strings as interchangeable with binary blobs, but
  not so for unicode strings. The webapp2 framework treats all incoming requests
  as unicode, se we need to cerce blobs to ASCII strings before storing them.
  """

  def _validate(self, value):
    return str(value)


class Trivial(ndb.Model):
  pass


class Blob(ndb.Model):
  blob = BlobProperty(required=True)


class AudioOutput(ndb.Model):
  pass


class DesignateUser(ndb.Model):
  uid = ndb.IntegerProperty(required=True)
