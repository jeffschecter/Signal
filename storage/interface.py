"""Interface for retrieving and writing data."""

import datetime

from google.appengine.ext import ndb
from storage import model


@ndb.transactional(xg=True)
def CreateAccount(name, latitude, longitude, country, region, city, now=None):
  """Create a new account.
  """
  # Prep objects for insertion
  now = now or datetime.datetime.today()
  user = model.User(name=name, joined=now)
  match = model.MatchParameters(
    id=1, parent=user.key, last_activity=now,
    latitude=latitude, longitude=longitude,
    country=country, region=region, city=city)
  search = model.SearchSettings(id=1, parent=user.key)

  # Send updates to the db
  user.put()
  match.put()
  search.put()
  return user, match, search


@ndb.transactional
def UpdateAccount(uid, **kwargs):
  """Update's a users User, MatchParameters, and SearchSettings objects.

  Args:
    uid: (int) The user's object id.
    **kwargs: (dict) Mapping properties to be updated to values.

  Returns:
    (model.User, model.MatchParameters, model.SearchSettings) The newly
    updated objects.
  """
  # Load the needed objects
  user_key = ndb.Key(model.User, uid)
  user, match, search = user_key.get(), None, None
  if not user:
    raise LookupError("User {u} does not exist.".format(u=uid))
  for argname, val in kwargs:
    if argname in (
        "joined", "last_activity"
        "latitude", "longitude", "country", "region", "city"):
      raise ValueError(
        "You can't set {a} in UpdateAccount.".format(a=argname))
    elif argname in model.User._properties:
      setattr(user, argname, val)
    elif argname in model.MatchParameters._properties:
      if not match:
        match = model.MatchParameters.get_by_id(1, parent=user_key)
      setattr(match, argname, val)
    elif argname in model.SearchSettings._properties:
      if not search:
        search = model.SearchSettings.get_by_id(1, parent=user_key)
      setattr(search, argname, val)
    else:
      raise ValueError(
        "'{a}' not found in User, MatchParameters, or SearchSettings".format(
          a=argname))

  # Send updates to the db.
  for entity in (user, match, search):
    if entity:
      entity.put()

  # Return changed objects
  return user, match, search


@ndb.transactional
def Ping(uid, latitude, longitude, country, region, city):
  """Set's a user's location and last active date.

  Args:
    uid: (int) The user's object id.
    latitude: (float) Degress latitude.
    longitude: (float) Degrees longitude.

  Returns:
    (model.MatchParameters) The newly updated match params.
  """
  user_key = ndb.Key(model.User, uid)
  match = model.MatchParameters.get_by_id(1, parent=user_key)
  if not match:
    raise LookupError("User {u} is incomplete.".format(u=uid))
  match.latitude = latitude
  match.longitude = longitude
  match.country = country
  match.region = region
  match.city = city
  match.last_activity = datetime.datetime.today()
  match.put()
  return match


@ndb.transactional
def LoadAccount(uid):
  """Loads all of a user's account info.

  Args:
    uid: (int) The user's object id.

  Returns:
    (dict) Account information.
  """
  user = model.User.get_by_id(uid)
  match = model.MatchParameters.get_by_id(1, parent=user.key)
  search = model.SearchSettings.get_by_id(1, parent=user.key)
  if not user and match and search:
    raise LookupError("User {u} is incomplete.".format(u=uid))
  return user, match, search
