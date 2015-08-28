"""Interface for retrieving and writing data to Datastore."""

import common
import datetime

from google.appengine.ext import ndb
from storage import model


# --------------------------------------------------------------------------- #
# Some utilities.                                                             #
# --------------------------------------------------------------------------- #

def Guarantee(obj):
  """Complains if the input is None, else passes it straight through.

  Args:
    obj: (*) The object to check.

  Returns:
    The object.

  Raises:
    (LookupError) If the object is None.
  """
  if obj is None:
    raise LookupError("Expected to retrieve datastore object but got None")
  return obj


def UKey(uid):
  """Returns the key for a model.User object with the given user id.

  Args:
    uid: (int) The user's object id.

  Returns:
    (ndb.Key) The user key.
  """
  return ndb.Key(model.User, uid)


def GetUser(uid):
  """Retrieves the model.User object for a given user id from the datastore.

  Args:
    uid: (int) The user's object id.

  Returns:
    (model.User) The user object.
  """
  return Guarantee(model.User.get_by_id(uid))


def GetForUid(model_class, uid):
  """Retrieves a model.* for a given user id from the datastore.

  This only works for model classes that are in a 1-to-1 relationship with the
  user, like the Garden; it doesn't work for say Relationship or Rose.

  Args:
    model_class: (class) A subclass of ndb.Model.
    uid: (int) The user's object id.

  Returns:
    (model_class) The retrieved model.
  """
  return Guarantee(model_class.get_by_id(1, parent=UKey(uid)))


def Relationship(agent, patient, full=True):
  """Retrieves or creates a relationship for two users.

  Note: If the relationship doesn't exist yet, nothing is written to the db by
  this function.

  Args:
    agent: (int) The user object id of the actor or sender.
    patient: (int) The user object id of the patient or recipient.
    full: (bool) True to access the full relationship.

  Returns:
    (model.Relationship or model.FullRelationship) The relationship.
  """
  if agent == patient:
    raise ValueError("A user has no relationship with itself.")
  cls = model.FullRelationship if full else model.Relationship
  obj = cls(id=patient, parent=UKey(agent))
  retrieved = obj.key.get()
  if retrieved is not None:
    return retrieved
  else:
    return obj


def Relationships(sender, recipient, full=True):
  """Retrieves a pair of relationships for two users, from each perspective.

  Args:
    sender: (int) The user object id of the arbitrarily chosen sender.
    recipient: (int) The user object id of the arbitrarily chosen recipient.
    full: (bool) True to access the full relationship.

  Returns:
    (pair of model.Relationship or model.FullRelationship) The relationships;
    with the "sender" in the agent roll in the first element, and the "patient"
    in the agent roll in the second.
  """
  return (Relationship(sender, recipient, full=full),
          Relationship(recipient, sender, full=full))


def GetForRelationship(model_class, agent, patient, ts):
  """Retrieves a model.* for a given rel. and timestmap from the datastore.

  This only works for objects that have a relationship as their ancestor and
  are keyed by timestamp, including SentMessage, ReceivedMessage, SentRose,
  ReceivedRose, and MessageFile.

  Args:
    model_class: (class) A subclass of ndb.Model.
    agent: (int) The user object id of the agent.
    patient: (int) The user object id of the patient.
    ts: (int or datetime.datetime) Timestamp of the object to be retrieved.

  Returns:
    (model_class) The retrieved model.
  """
  if agent == patient:
    raise ValueError("A user has no relationship with itself.")
  assert isinstance(ts, (int, datetime.datetime))
  if isinstance(ts, datetime.datetime):
    ts = common.Milis(ts)
  parent_key = model.Relationship(id=patient, parent=UKey(agent)).key
  return Guarantee(model_class.get_by_id(ts, parent=parent_key))


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


# pylint: disable=no-value-for-parameter
@ndb.transactional(xg=True)
def CreateAccount(name, latitude, longitude, now=None):
  """Create a new account.

  Args:
    name: (str) The user's nickname.
    latitude: (float) Degress latitude.
    longitude: (float) Degress longitude.
    now: (datetime.datetime) To peg current time; for testing.

  Returns:
    (model.User, model.MatchParameters, model.SearchSettings) For the newly
    created user.
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
    kwargs: (dict) Mapping properties to be updated to values.

  Returns:
    (model.User, model.MatchParameters, model.SearchSettings) The newly
    updated objects.
  """
  # pylint: disable=protected-access
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


# --------------------------------------------------------------------------- #
# Working with messages.                                                      #
# --------------------------------------------------------------------------- #

# pylint: disable=no-value-for-parameter
@ndb.transactional(xg=True)
def SendMessage(sender, recipient, blob, now=None):
  """Sends a message from one user to another.

  Args:
    sender: (int) The user object id of the sender.
    recipient: (int) The user object id of the recipient.
    blob: (str) Raw AAC file bytestring.
    now: (datetime.datetime) To peg current time; for testing.

  Returns:
    (datetime.datetime) The timestamp assigned to the message.
  """
  now = now or datetime.datetime.today()
  ts = common.Milis(now)
  sender_rel, recipient_rel = Relationships(sender, recipient, full=True)

  # Save the actual audio
  model.MessageFile(id=ts, parent=sender_rel.key, blob=blob).put()

  # Save a trace in both the sender ad recipient's relationship
  model.SentMessage(id=ts, parent=sender_rel.key).put()
  model.ReceivedMessage(id=ts, parent=recipient_rel.key).put()

  # Update the last sent and last received message fields in the relationships
  sender_rel.last_sent_message = now
  sender_rel.put()
  recipient_rel.last_received_message = now
  recipient_rel.new_messages += 1
  recipient_rel.put()

  return now


# pylint: disable=no-value-for-parameter
@ndb.transactional(xg=True)
def GetMessageFile(sender, recipient, send_time, record_retrieval, now=None):
  """Retrieves the audio of a message.

  Args:
    sender: (int) The user object id of the sender.
    recipient: (int) The user object id of the recipient.
    send_time: (int or datetime.datetime) The message timestamp.
    record_retrieval: (bool) If true, unmark the message as new and record
      when it was retrieved.
    now: (datetime.datetime) To peg current time; for testing.

  Returns:
    (str) Raw aac file bytestring.
  """
  now = now or datetime.datetime.today()
  blob = GetForRelationship(
      model.MessageFile, sender, recipient, send_time).blob

  # Record the tretrieval
  if record_retrieval:
    sent_msg = GetForRelationship(
        model.SentMessage, sender, recipient, send_time)
    rcvd_msg = GetForRelationship(
        model.ReceivedMessage, recipient, sender, send_time)
    if rcvd_msg.new:
      recipient_rel = Relationship(recipient, sender)
      recipient_rel.new_messages -= 1
      recipient_rel.put()
    for msg in (sent_msg, rcvd_msg):
      msg.new = False
      msg.retrieved.append(now)
      msg.put()

  return blob
