"""Endpoints for working with a user's garden."""

from handlers import util


class Load(util.AuthedHandler):
  def Handle(self):
    util.TODO()


class Send(util.AuthedHandler):
  def Handle(self):
    util.TODO()


class Water(util.AuthedHandler):
  def Handle(self):
    util.TODO()


ROUTES = (
  ('/garden/load/*', Load),
  ('/garden/send/*', Send),
  ('/garden/Water/*', Water),
  )
