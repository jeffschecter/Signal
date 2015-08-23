"""Endpoints for working with a user's account."""

from google.appengine.ext import ndb
from handlers.lib import ioformat
from handlers.lib import util
from storage import interface
from storage import model


ROUTES = []


# --------------------------------------------------------------------------- #
# Create a new account.                                                       #
# --------------------------------------------------------------------------- #

class CreateInformat(ndb.Model):
  name = ndb.StringProperty(required=True)


class CreateOutformat(ndb.Model):
  uid = ndb.IntegerProperty(required=True)


class Create(util.RequestHandler):

  in_format = CreateInformat
  out_format = CreateOutformat

  def Handle(self):
    user, unused_match, unused_search = interface.CreateAccount(
      self.GetArg("name"),
      self.GetEnv("latitude"),
      self.GetEnv("longitude"))
    self.UpdateArgs(uid=user.key.id())

ROUTES.append(('/account/create/*', Create))


# --------------------------------------------------------------------------- #
# Load account info.                                                          #
# --------------------------------------------------------------------------- #

class LoadOutformat(ndb.Model):
  uid = ndb.IntegerProperty(required=True)
  name = ndb.StringProperty()
  gender_string = ndb.StringProperty()  # If MatchParameters.gender == 2
  sexuality_string = ndb.StringProperty()  # If MatchParameters.sexuality == 3
  joined = ndb.DateTimeProperty()
  gender = ndb.IntegerProperty()  # 0=male, 1=female, 2=other
  sexuality = ndb.IntegerProperty()  # 0=gay, 1=straight, 2=bi, 3=other
  birthday = ndb.DateTimeProperty()
  last_activity = ndb.DateTimeProperty()
  latitude = ndb.FloatProperty()
  longitude = ndb.FloatProperty()
  active = ndb.BooleanProperty()
  radius = ndb.FloatProperty()  # In miles
  min_age = ndb.IntegerProperty()  # In years
  max_age = ndb.IntegerProperty()  # In years
  accept_male_sexualities = ndb.IntegerProperty(repeated=True)
  accept_female_sexualities = ndb.IntegerProperty(repeated=True)
  accept_other_sexualities = ndb.IntegerProperty(repeated=True)


class Load(util.AuthedHandler):

  in_format = ioformat.Trivial
  out_format = LoadOutformat

  def Handle(self):
    user, match, search = interface.LoadAccount(self.GetEnv("uid"))
    self.UpdateArgs(user, match, search, uid=user.key.id())

ROUTES.append(('/account/load/*', Load))


# --------------------------------------------------------------------------- #
# Upload your audio introduction.                                             #
# --------------------------------------------------------------------------- #

class SetIntroOutformat(ndb.Model):
  pass

class SetIntro(util.AuthedHandler):

  in_format = ioformat.Blob
  out_format = SetIntroOutformat

  def Handle(self):
    util.TODO()

ROUTES.append(('/account/set_intro/*', SetIntro))


# --------------------------------------------------------------------------- #
# Set your chat imge.                                                         #
# --------------------------------------------------------------------------- #

class SetImageOutformat(ndb.Model):
  pass


class SetImage(util.AuthedHandler):

  in_format = ioformat.Blob
  out_format = SetImageOutformat

  def Handle(self):
    util.TODO()

ROUTES.append(('/account/set_image/*', SetImage))


# --------------------------------------------------------------------------- #
# Set your personal information.                                              #
# --------------------------------------------------------------------------- #

class BioInformat(ndb.Model):
  gender = ndb.IntegerProperty(required=True)
  gender_string = ndb.StringProperty()
  sexuality = ndb.IntegerProperty(required=True)
  sexuality_string = ndb.StringProperty()


class BioOutformat(ndb.Model):
  pass


class Bio(util.AuthedHandler):

  in_format = BioInformat
  out_format = BioOutformat

  def Handle(self):
    util.TODO()

ROUTES.append(('/account/bio/*', Bio))


# --------------------------------------------------------------------------- #
# Set your potential match search preferences.                                #
# --------------------------------------------------------------------------- #

class Preferences(util.AuthedHandler):

  in_format = model.SearchSettings
  out_format = model.SearchSettings

  def Handle(self):
    util.TODO()

ROUTES.append(('/account/preferences/*', Preferences))


# --------------------------------------------------------------------------- #
# Deactivate your account.                                                    #
# --------------------------------------------------------------------------- #

class Deactivate(util.AuthedHandler):

  in_format = ioformat.Trivial
  out_format = ioformat.Trivial

  def Handle(self):
    interface.UpdateAccount(
      self.GetEnv("uid"),
      active=False)

ROUTES.append(('/account/deactivate/*', Deactivate))


# --------------------------------------------------------------------------- #
# Reactivate your account.                                                    #
# --------------------------------------------------------------------------- #

class Reactivate(util.AuthedHandler):

  in_format = ioformat.Trivial
  out_format = ioformat.Trivial

  def Handle(self):
    interface.UpdateAccount(
      self.GetEnv("uid"),
      active=True)

ROUTES.append(('/account/reactivate/*', Reactivate))


# --------------------------------------------------------------------------- #
# Log out of your account.                                                    #
# --------------------------------------------------------------------------- #

class Logout(util.AuthedHandler):

  in_format = ioformat.Trivial
  out_format = ioformat.Trivial

  def Handle(self):
    util.TODO()

ROUTES.append(('/account/logout/*', Logout))


# --------------------------------------------------------------------------- #
# Send current location.                                                      #
# --------------------------------------------------------------------------- #

class PingOutformat(ndb.Model):
  latitude = ndb.FloatProperty(required=True)
  longitude = ndb.FloatProperty(required=True)
  country = ndb.StringProperty(required=True)
  region = ndb.StringProperty(required=True)
  city = ndb.StringProperty(required=True)


class Ping(util.AuthedHandler):

  in_format = ioformat.Trivial
  out_format = PingOutformat

  def Handle(self):
    match = interface.Ping(
      self.GetEnv("uid"),
      self.GetEnv("latitude"),
      self.GetEnv("longitude"))
    self.SetArg("latitude", match.latitude)
    self.SetArg("longitude", match.longitude)
    util.TODO()  # country, region, city

ROUTES.append(('/account/ping/*', Ping))
