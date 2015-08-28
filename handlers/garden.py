# pylint: disable=missing-docstring

"""Endpoints for working with a user"s garden."""

from google.appengine.ext import ndb
from handlers.lib import ioformat
from handlers.lib import util
from storage import interface
from storage import model


ROUTES = []


# --------------------------------------------------------------------------- #
# Load the user"s garden.                                                     #
# --------------------------------------------------------------------------- #

class LoadOutformat(ndb.Model):
  roses = ndb.StructuredProperty(model.Rose, repeated=True)


class Load(util.AuthedHandler):

  in_format = ioformat.Trivial
  out_format = LoadOutformat

  def _VerifyOut(self):
    assert len(self.response_args["roses"]) ==  3, (
        "Expected 3 roses in the garden.")

  def Handle(self):
    self.SetArg("roses", interface.GetGarden(self.GetEnv("uid")))

ROUTES.append(("/garden/load/*", Load))


# --------------------------------------------------------------------------- #
# Send a rose.                                                                #
# --------------------------------------------------------------------------- #

class SendInformat(ndb.Model):
  recipient = ndb.IntegerProperty(required=True)
  rose_number = ndb.IntegerProperty(required=True)


class SendOutformat(ndb.Model):
  success = ndb.BooleanProperty(required=True)
  roses = ndb.StructuredProperty(model.Rose, repeated=True)


class Send(util.AuthedHandler):

  in_format = SendInformat
  out_format = SendOutformat

  def _VerifyOut(self):
    if self.GetArg("success"):
      assert len(self.GetArg("roses")) == 3, "Expected 3 roses in the garden."
    else:
      assert not self.GetArg("roses"), "Expected 0 roses in the garden."

  def Handle(self):
    uid = self.GetEnv("uid")
    success = interface.SendRose(
        uid,
        self.GetArg("recipient"),
        self.GetArg("rose_number"))
    self.SetArg("success", bool(success))
    if success:
      self.SetArg("roses", interface.GetGarden(uid))

ROUTES.append(("/garden/send/*", Send))


# --------------------------------------------------------------------------- #
# Water your garden.                                                          #
# --------------------------------------------------------------------------- #

class WaterInformat(ndb.Model):
  pass


class WaterOutformat(ndb.Model):
  pass


class Water(util.AuthedHandler):

  in_format = WaterInformat
  out_format = WaterOutformat

  def Handle(self):
    util.TODO()

ROUTES.append(("/garden/water/*", Water))
