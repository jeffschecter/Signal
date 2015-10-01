# pylint: disable=missing-docstring

"""Endpoints for working with a user's history."""

from google.appengine.ext import ndb
from handlers.lib import ioformat
from handlers.lib import util
from storage import interface
from storage import model


ROUTES = []


# --------------------------------------------------------------------------- #
# Load relationship action history, including visits, roses, & messages.      #
# --------------------------------------------------------------------------- #

class LoadInformat(ndb.Model):
  offset = ndb.IntegerProperty()
  limit = ndb.IntegerProperty()
  cache_time = ndb.DateTimeProperty()
  ascending = ndb.BooleanProperty()
  new = ndb.BooleanProperty()
  saved_only = ndb.BooleanProperty()
  blocked_only = ndb.BooleanProperty()
  sent_rose_only = ndb.BooleanProperty()
  reeived_rose_only = ndb.BooleanProperty()
  sent_message_only = ndb.BooleanProperty()
  received_message_property = ndb.BooleanProperty()
  visited_only = ndb.BooleanProperty()
  visited_by_ony = ndb.BooleanProperty()


class LoadOutformat(ndb.Model):
  pass


class Load(util.AuthedHandler):

  in_format = LoadInformat
  out_format = LoadOutformat

  def Handle(self):
    util.TODO()
    history = interface.History(self.GetEnv("uid"), **self.args)


ROUTES.append(("/history/load/*", Load))
