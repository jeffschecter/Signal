"""Endpoints for working with profile browsing."""

from handlers import util


class Load(util.AuthedHandler):
  def Handle(self):
    util.TODO()


class Next(util.AuthedHandler):
  def Handle(self):
    util.TODO()


class Listen(util.AuthedHandler):
  def Handle(self):
    util.TODO()


class Save(util.AuthedHandler):
  def Handle(self):
    util.TODO()


class Unsave(util.AuthedHandler):
  def Handle(self):
    util.TODO()


class Block(util.AuthedHandler):
  def Handle(self):
    util.TODO()


class Unblock(util.AuthedHandler):
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
