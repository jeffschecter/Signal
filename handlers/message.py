"""Endpoints for working with a user's messages."""

from google.appengine.ext import ndb
from handlers.lib import ioformat
from handlers.lib import util
from storage import interface
from storage import model


ROUTES = []


# --------------------------------------------------------------------------- #
# Retrieve the audio file for a message.                                      #
# --------------------------------------------------------------------------- #

class ListenInformat(ndb.Model):
  profile = ndb.IntegerProperty(required=True)
  message = ndb.IntegerProperty(required=True)


class Listen(util.AuthedHandler):

  in_format = ListenInformat
  out_format = ioformat.AudioOutput

  def Handle(self):
    util.TODO()

ROUTES.append(('/message/listen/*', Listen))


# --------------------------------------------------------------------------- #
# Send a user an audio message.                                               #
# --------------------------------------------------------------------------- #

class SendInformat(ndb.Model):
  profile = ndb.IntegerProperty(required=True)
  blob = ioformat.BlobProperty(required=True)


class Send(util.AuthedHandler):

  in_format = SendInformat
  out_format = ioformat.Trivial

  def Handle(self):
    util.TODO()

ROUTES.append(('/message/send/*', Send))
