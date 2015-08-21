"""Endpoints for working with a user's messages."""

from handlers import util


class Listen(util.AuthedHandler):
  def Handle(self):
    util.TODO()


class Send(util.AuthedHandler):
  def Handle(self):
    util.TODO()


ROUTES = (
  ('/message/listen/*', Listen),
  ('/message/send/*', Send),
  )
