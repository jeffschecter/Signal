# pylint: disable=missing-docstring

"""Endpoints for working with a user's messages."""

import common

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
  sender = ndb.IntegerProperty(required=True)
  recipient = ndb.IntegerProperty(required=True)
  send_timestamp_ms = ndb.IntegerProperty(required=True)


class Listen(util.AuthedHandler):

  in_format = ListenInformat

  def _VerifyIn(self):
    uid = self.GetEnv("uid")
    if uid not in (sender, recipient):
      raise util.VerificationError(
          "User {u} tried to listen to a message from {s} to {r}".format(
              u=uid, s=sender, r=recipient))

  def Handle(self):
    blob = interface.GetMessageFile(
        self.GetArg("sender"),
        self.GetArg("recipient"),
        self.GetArg("send_timestamp_ms"),
        True)
    return "", blob

ROUTES.append(('/message/listen/*', Listen))


# --------------------------------------------------------------------------- #
# Send a user an audio message.                                               #
# --------------------------------------------------------------------------- #

class SendInformat(ndb.Model):
  recipient = ndb.IntegerProperty(required=True)
  blob = ioformat.BlobProperty(required=True)


class SendOutformat(ndb.Model):
  send_timestamp_ms = ndb.IntegerProperty(required=True)


class Send(util.FileAcceptingAuthedHandler):

  in_format = SendInformat
  out_format = SendOutformat

  def Handle(self):
    send_time = interface.SendMessage(
        self.GetEnv("uid"),
        self.GetArg("recipient"),
        self.file)
    self.SetArg("send_timestamp_ms", common.Milis(send_time))

ROUTES.append(('/message/send/*', Send))
