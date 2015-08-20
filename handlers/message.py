"""Endpoints for working with a user's messages."""

from handlers import util


class Listen(util.RequestHandler):
  def Handle(self):
    util.TODO()


class Send(util.RequestHandler):
  def Handle(self):
    util.TODO()


ROUTES = (
  ('/message/listen/*', Listen),
  ('/message/send/*', Send),
  )
