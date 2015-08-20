"""Endpoints for working with profile browsing."""

from handlers import util


class Load(util.RequestHandler):
  def Handle(self):
    util.TODO()


class Next(util.RequestHandler):
  def Handle(self):
    util.TODO()


class Listen(util.RequestHandler):
  def Handle(self):
    util.TODO()


class Save(util.RequestHandler):
  def Handle(self):
    util.TODO()


class Unsave(util.RequestHandler):
  def Handle(self):
    util.TODO()


class Block(util.RequestHandler):
  def Handle(self):
    util.TODO()


class Unblock(util.RequestHandler):
  def Handle(self):
    util.TODO()


ROUTES = (
  ('/profile/load/*', Load),
  ('/profile/next/*', Next),
  ('/profile/listen/*', Listen),
  ('/profile/save/*', Save),
  ('/profile/unsave/*', Unsave),
  ('/profile/block/*', Block),
  ('/profile/unblock/*', Unblock),
  )
