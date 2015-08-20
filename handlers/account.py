"""Endpoints for working with a user's account."""

from handlers import util


class Load(util.RequestHandler):
  def Handle(self):
    util.TODO()


class SetIntro(util.RequestHandler):
  def Handle(self):
    util.TODO()


class SetImage(util.RequestHandler):
  def Handle(self):
    util.TODO()


class Bio(util.RequestHandler):
  def Handle(self):
    util.TODO()


class Preferences(util.RequestHandler):
  def Handle(self):
    util.TODO()


class Deactivate(util.RequestHandler):
  def Handle(self):
    util.TODO()


class Reactivate(util.RequestHandler):
  def Handle(self):
    util.TODO()


class Logout(util.RequestHandler):
  def Handle(self):
    util.TODO()


class Location(util.RequestHandler):
  def Handle(self):
    util.TODO()


ROUTES = (
  ('/account/load/*', Load),
  ('/account/set_intro/*', SetIntro),
  ('/account/set_image/*', SetImage),
  ('/account/bio/*', Bio),
  ('/account/preferences/*', Preferences),
  ('/account/deactivate/*', Deactivate),
  ('/account/reactivate/*', Reactivate),
  ('/account/logout/*', Logout),
  ('/account/location/*', Location),
  )
