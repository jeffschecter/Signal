"""Endpoints for working with a user's garden."""

from handlers import util


class Load(util.RequestHandler):
  def Handle(self):
    util.TODO()


class Send(util.RequestHandler):
  def Handle(self):
    util.TODO()


class Water(util.RequestHandler):
  def Handle(self):
    util.TODO()


ROUTES = (
  ('/garden/load/*', Load),
  ('/garden/send/*', Send),
  ('/garden/Water/*', Water),
  )