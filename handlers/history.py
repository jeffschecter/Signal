"""Endpoints for working with a user's history."""

from handlers import util


class Load(util.AuthedHandler):
  def Handle(self):
    util.TODO()


ROUTES = (
  ('/history/load/*', Load),
  )
