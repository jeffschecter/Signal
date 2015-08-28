# pylint: disable=missing-docstring

"""Endpoints for working with a user"s history."""

from google.appengine.ext import ndb
from handlers.lib import ioformat
from handlers.lib import util
from storage import interface
from storage import model


ROUTES = []


# --------------------------------------------------------------------------- #
# Load relationship action history, including visits, roses, & messages.      #
# --------------------------------------------------------------------------- #

class LoadOutformat(ndb.Model):
  pass


class Load(util.AuthedHandler):

  in_format = ioformat.Trivial
  out_format = LoadOutformat

  def Handle(self):
    util.TODO()

ROUTES.append(("/history/load/*", Load))
