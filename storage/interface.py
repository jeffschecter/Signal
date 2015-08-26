"""Interface for retrieving and writing data to Datastore."""

import datetime

from google.appengine.ext import ndb
from storage import model


# --------------------------------------------------------------------------- #
# Some utilities.                                                             #
# --------------------------------------------------------------------------- #

def Guarantee(obj):
  if obj is None:
    raise LookupError("Expected to retrieve datastore object but got None")
  return obj


def UKey(uid):
  return ndb.Key(model.User, uid)


def GetUser(uid):
  return Guarantee(model.User.get_by_id(uid))


def GetForUid(model_class, uid):
  return Guarantee(model_class.get_by_id(1, parent=UKey(uid)))


# --------------------------------------------------------------------------- #
# Working with user accounts.                                                 #
# --------------------------------------------------------------------------- #

def LoadAccount(uid):
  """Loads all of a user's account info.

  Args:
    uid: (int) The user's object id.

  Returns:
    (dict) Account information.
  """
  user = GetUser(uid)
  match = GetForUid(model.MatchParameters, uid)
  search = GetForUid(model.SearchSettings, uid)
  return user, match, search


@ndb.transactional(xg=True)
def CreateAccount(name, latitude, longitude, now=None):
  """Create a new account.
  """
  now = now or datetime.datetime.today()
  user = model.User(name=name, joined=now)
  user.put()
  match = model.MatchParameters(
    id=1, parent=user.key, last_activity=now,
    latitude=latitude, longitude=longitude)
  match.put()
  search = model.SearchSettings(id=1, parent=user.key)
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
  user, match, search = None, None, None
  for argname, val in kwargs.iteritems():
    if argname in ("joined", "last_activity", "latitude", "longitude"):
      raise ValueError(
        "You can't set {a} in UpdateAccount.".format(a=argname))
    elif argname in model.User._properties:
      if not user:
        user = GetUser(uid)
      setattr(user, argname, val)
    elif argname in model.MatchParameters._properties:
      if not match:
        match = GetForUid(model.MatchParameters, uid)
      setattr(match, argname, val)
    elif argname in model.SearchSettings._properties:
      if not search:
        search = GetForUid(model.SearchSettings, uid)
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


def Ping(uid, latitude, longitude):
  """Sets a user's location and last active date.

  Args:
    uid: (int) The user's object id.
    latitude: (float) Degress latitude.
    longitude: (float) Degrees longitude.

  Returns:
    (model.MatchParameters) The newly updated match params.
  """
  match = GetForUid(model.MatchParameters, uid)
  match.latitude = latitude
  match.longitude = longitude
  match.last_activity = datetime.datetime.today()
  match.put()
  return match


def SetIntro(uid, blob):
  """Sets a user's audio intro.

  Args:
    uid: (int) The user's object id.
    blob: (unicode) Raw AAC file bytestring.
  """
  blob = str(blob)
  #TODO validate file format and size
  user_key = UKey(uid)
  intro = model.IntroFile(id=1, parent=user_key, blob=blob)
  intro.put()


def GetIntro(uid):
  """Gets a user's audio intro.

  Args:
    uid: (int) The user's object id.

  Returns:
    (str) Raw AAC file bytestring
  """
  return GetForUid(model.IntroFile, uid).blob


def SetImage(uid, blob):
  """Sets a user's chat image.

  Args:
    uid: (int) The user's object id.
    blob: (unicode) Raw png file bytestring.
  """
  blob = str(blob)
  #TODO validate file format and size, and image dimensions
  user_key = UKey(uid)
  image = model.ImageFile(id=1, parent=user_key, blob=blob)
  image.put()


def GetImage(uid):
  """Gets a user's chat image.

  Args:
    uid: (int) The user's object id.

  Returns:
    (str) Raw png file bytestring
  """
  return GetForUid(model.ImageFile, uid).blob
