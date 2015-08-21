"""Endpoints for working with a user's account."""

from common import lib
from handlers import util
from storage import interface


class Create(util.RequestHandler):
  def Handle(self):
    objs = interface.CreateAccount(
      self.Arg("name"),
      self.Env("latitude"),
      self.Env("longitude"))
    self.Set("info", lib.MergeModelsToDict(
      *objs,
      uid=objs[0].key.id()))


class Load(util.AuthedHandler):
  def Handle(self):
    objs = interface.LoadAccount(self.Env("uid"))
    self.Set("info", lib.MergeModelsToDict(
      *objs,
      uid=info[0].key.id()))


class SetIntro(util.AuthedHandler):
  def Handle(self):
    util.TODO()


class SetImage(util.AuthedHandler):
  def Handle(self):
    util.TODO()


class Bio(util.AuthedHandler):
  def Handle(self):
    util.TODO()


class Preferences(util.AuthedHandler):
  def Handle(self):
    util.TODO()


class Deactivate(util.AuthedHandler):
  def Handle(self):
    interface.UpdateAccount(
      self.Env("uid"),
      active=False)


class Reactivate(util.AuthedHandler):
  def Handle(self):
    interface.UpdateAccount(
      self.Env("uid"),
      active=True)
    

class Logout(util.AuthedHandler):
  def Handle(self):
    util.TODO()


class Ping(util.AuthedHandler):
  def Handle(self):
    interface.Ping(
      self.Env("uid"),
      self.Env("latitude"),
      self.Env("longitude"))


ROUTES = (
  ('/account/create/*', Create),
  ('/account/load/*', Load),
  ('/account/set_intro/*', SetIntro),
  ('/account/set_image/*', SetImage),
  ('/account/bio/*', Bio),
  ('/account/preferences/*', Preferences),
  ('/account/deactivate/*', Deactivate),
  ('/account/reactivate/*', Reactivate),
  ('/account/logout/*', Logout),
  ('/account/ping/*', Ping),
  )
