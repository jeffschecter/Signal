# pylint: disable=missing-docstring

"""Endpoints for working with a user's garden."""

from google.appengine.ext import ndb
from handlers.lib import ioformat
from handlers.lib import util
from storage import interface
from storage import model


ROUTES = []


# --------------------------------------------------------------------------- #
# Load the user's garden.                                                     #
# --------------------------------------------------------------------------- #

class LoadOutformat(ndb.Model):
  pass


class Load(util.AuthedHandler):

  in_format = ioformat.Trivial
  out_format = LoadOutformat

  def Handle(self):
    util.TODO()

ROUTES.append(('/garden/load/*', Load))


# --------------------------------------------------------------------------- #
# Send a rose.                                                                #
# --------------------------------------------------------------------------- #

class SendInformat(ndb.Model):
  partner = ndb.IntegerProperty(required=True)
  rose = ndb.IntegerProperty(required=True)


class SendOutformat(ndb.Model):
  pass


class Send(util.AuthedHandler):

  in_format = SendInformat
  out_format = SendOutformat

  def Handle(self):
    util.TODO()

ROUTES.append(('/garden/send/*', Send))


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

ROUTES.append(('/garden/water/*', Water))
