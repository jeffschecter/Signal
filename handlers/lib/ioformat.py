"""Endpoint input formats."""

from google.appengine.ext import ndb


class BigBlobProperty(ndb.BlobProperty):

  def _validate(self, value):
    return ""


class Trivial(ndb.Model):
  pass


class Blob(ndb.Model):
  blob = BigBlobProperty(required=True)


class AudioOutput(ndb.Model):
  pass


class DesignateUser(ndb.Model):
  uid = ndb.IntegerProperty(required=True)
