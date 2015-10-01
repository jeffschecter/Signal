"""Interface for retrieving and writing data to Datastore."""

import common
import datetime
import random

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
  """Retrieves a model.* for a given rel. and timestamp from the datastore.

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
    now: (datetime.datetime) To peg the current time; for testing.

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

  # Plant the garden
  rose_kwargs = {
      "parent": model.Garden(id=1, parent=user.key).key,
      "bloomed": now,
      "planted": now}
  model.Rose(id=1, **rose_kwargs).put()
  model.Rose(id=2, **rose_kwargs).put()
  model.Rose(id=3, **rose_kwargs).put()

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

def CanMessage(sender_rel, recipient_rel):
  """Determines whether one user is allowed to message another.

  Args:
    sender_rel: (model.Relationship) With sender as agent.
    recipient_rel: (model.Relationship) With recipient as agent.

  Returns:
    (bool) True if the sender is allowed to message the recipient.
  """
  #TODO
  return True


# pylint: disable=no-value-for-parameter
@ndb.transactional(xg=True)
def SendMessage(sender, recipient, blob, now=None):
  """Sends a message from one user to another.

  Args:
    sender: (int) The user object id of the sender.
    recipient: (int) The user object id of the recipient.
    blob: (str) Raw AAC file bytestring.
    now: (datetime.datetime) To peg the current time; for testing.

  Returns:
    (datetime.datetime or None) Send time, or None if sending failed.
  """
  assert sender != recipient, "User {u} tried to message itself.".format(
      u=sender)
  now = now or datetime.datetime.today()
  ts = common.Milis(now)
  sender_rel, recipient_rel = Relationships(sender, recipient, full=True)

  # Check that the message is allowed.
  if not CanMessage(sender_rel, recipient_rel):
    return

  # Save the actual audio
  model.MessageFile(id=ts, parent=sender_rel.key, blob=blob).put()

  # Save a trace in both the sender and recipients' relationships
  model.SentMessage(id=ts, parent=sender_rel.key).put()
  model.ReceivedMessage(id=ts, parent=recipient_rel.key).put()

  # Update the last sent and last received message fields in the relationships
  sender_rel.last_sent_message = max(sender_rel.last_sent_message, now)
  sender_rel.put()
  recipient_rel.last_received_message = max(
      recipient_rel.last_received_message, now)
  recipient_rel.last_incoming = max(recipient_rel.last_incoming, now)
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
    now: (datetime.datetime) To peg the current time; for testing.

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


# --------------------------------------------------------------------------- #
# Working with the garden.                                                    #
# --------------------------------------------------------------------------- #

def RandomGrowingPeriod():
  """Random growing time that averages one day.

  Returns:
    (datetime.timedelta) Time required for a new rose to grow!
  """
  hours = random.choice([
      random.expovariate(1) + 1,   # Just a few hours
      random.gauss(22.75, 1.5),   # About one day
      random.gauss(46.75, 1.5)])  # About two days
  return datetime.timedelta(hours=hours)


def GetGrowingRose(uid, rose_number):
  """Gets the given growing rose.

  Args:
    uid: (int) The user object id of the user to fetch a rose for.
    rose_number: (int) The id of the rose to get; 1, 2, or 3.

  Returns:
    (model.Rose) The rose.
  """
  assert rose_number in (1, 2, 3), "Rose number must be 1, 2, or 3."
  return Guarantee(model.Rose.get_by_id(
      id=rose_number, parent=model.Garden(id=1, parent=UKey(uid)).key))


def GetGarden(uid):
  """Returns all of a user's growing roses.

  Args:
    uid: (int) The user object id.

  Returns:
    (triple of model.Rose) The roses.
  """
  return [GetGrowingRose(uid, i) for i in (1, 2, 3)]



@ndb.transactional(xg=True)
def SendRose(sender, recipient, rose_number, now=None):
  """Sends a rose from the sender to the recipient, if possible.

  Args:
    sender: (int) The user object id of the sender.
    recipient: (int) The user object id of the recipient.
    rose_number: (int) The id of the rose to send.
    now: (datetime.datetime) To peg the current time; for testing.

  Returns:
    (datetime.datetime or None) Send time, or None if sending failed.
  """
  assert sender != recipient, "User {u} tried to send itself a rose.".format(
      u=sender)
  now = now or datetime.datetime.today()
  growing_rose = GetGrowingRose(sender, rose_number)

  # Sending fails if the rose has yet to bloom.
  if growing_rose.bloomed > now:
    return

  # Save a trace in both the sender and recipients' relationships
  ts = common.Milis(now)
  sender_rel, recipient_rel = Relationships(sender, recipient, full=True)
  rose_kwargs = {
      "id": ts,
      "bloomed": growing_rose.bloomed,
      "planted": growing_rose.planted}
  model.SentRose(parent=sender_rel.key, **rose_kwargs).put()
  model.ReceivedRose(parent=recipient_rel.key, **rose_kwargs).put()

  # Update the last sent and last received rose fields in the relationships
  sender_rel.last_sent_rose = max(sender_rel.last_sent_rose, now)
  sender_rel.put()
  recipient_rel.last_received_rose = max(recipient_rel.last_received_rose, now)
  recipient_rel.last_incoming = max(recipient_rel.last_incoming, now)
  recipient_rel.new_roses += 1
  recipient_rel.put()

  # Plant a new rose, to bloom on average one day later
  growing_rose.planeted = now
  growing_rose.bloomed = now + RandomGrowingPeriod()
  growing_rose.put()

  return now


@ndb.transactional(xg=True)
def Water(uid, kind, roses=None, **kwargs):
  """Bloom the rose with the longest remaining time to bloom.

  You can't water a rose that's scheduled to bloom within 10 minutes, or a rose
  that's already bloomed.

  Args:
    uid: (int) The user's object id
    kind: (int) 0 for paid, 1 for invite, 2 for lotto, ...
    roses: (triple of model.Rose) The user's garden.
    kwargs: (dict) Additional properties of the watering event.

  Returns:
    (int) The id of the bloomed rose, or None if no rose could be bloomed.
  """
  roses = roses or GetGarden(uid)
  now = datetime.datetime.today()
  greenest = max(roses, key=lambda rose: rose.bloomed)
  if greenest.bloomed - now < datetime.timedelta(minutes=10):
    return None

  # Update bloom time and record watering event
  greenest.bloomed = now
  greenest.put()
  watering = model.Watering(
      parent=model.Garden(id=1, parent=UKey(uid)).key,
      timestamp=now,
      kind=kind,
      **kwargs)
  watering.put()

  return greenest.key.id()


def EligibleForWatering(uid, roses=None):
  """Determines whether a user can water their garden.

  Args:
    uid: (int) The user's object id.
    roses: (triple of model.Rose) The user's garden.

  Returns:
    (bool) Whether the user is allowed to water their garden.
  """
  now = datetime.datetime.today()
  ts = common.Milis(now)
  for water in model.Watering.query(ancestor=UKey(uid)).iter(keys_only=True):
    if (ts - water.id()) < (24 * 60 * 60 * 1000):
      return False
  roses = roses or GetGarden(uid)
  greenest = max(roses, key=lambda rose: rose.bloomed)
  if greenest.bloomed - now < datetime.timedelta(minutes=10):
    return False
  return True


def MaybeWaterForPayment():
  raise NotImplementedError


def MaybeWaterForInvite():
  raise NotImplementedError


def MaybeWaterForLotto():
  raise NotImplementedError


# --------------------------------------------------------------------------- #
# Get a user's interaction history / "inbox".                                 #
# --------------------------------------------------------------------------- #

def History(uid, offset=0, limit=10, cache_time=None, ascending=False,
            new=False, saved_only=False, blocked_only=False,
            sent_rose_only=False, received_rose_only=False,
            sent_message_only=False, received_message_only=False,
            visited_only=False, visited_by_only=False):
  """Retrieves a summary of recent interactions for a user.

  Default sort order is descending by last incoming communication. When the
  query is limited to only sent or received roses or messages, sort order
  is descending by last sent or received rose or message, respectively. When
  limited to only profiles who the user visited or visited by, the last date
  of that interaction is used instead.

  Only one of the *_only args should be set.

  Args:
    uid: (int) The user's object id.
    offset: (int) Start at the offset'th most recent interaction.
    limit: (int) Retrieve the n most recent interactions.
    cache_time: (datetime.datetime) Retrieve only interactions with profiles
      that have been updated since this time.
    ascending: (bool) If true, sort in ascending order of date.
    new: (bool) Retrieve only interactions with profiles that have sent new
      unlistened messages or new roses.
    saved_only: (bool) Retrieve only interactions with saved profiles.
    blocked_only: (bool) Retrieve only interactions with blocked profiles; else,
      retrieved only interactions with non-blocked profiles.
    sent_rose_only: (bool) Retrieve only interactions with profiles to whom
      the user has sent a rose.
    received_rose_only: (bool) Retrieve only interactions with profiles from
      whom the user has received a rose.
    sent_message_only: (bool) Retrieve only interactions with profiles  to
      whom the user has sent a message.
    received_message_only: (bool) Retrieve only interactions with profiles
      from whom the user has received a message.
    visited_only: (bool) Retrieve only interactions with profiles whom the
      user has visited.
    visited_by_only: (bool) Retrieve only interactions with profiles that
      have visited the user.

  Returns:
    (list of dict) "Inbox" entries.
  """
  limit_args = (
      saved_only, blocked_only, sent_rose_only, received_rose_only,
      sent_message_only, received_message_only, visited_only, visited_by_only)
  assert sum(limit_args) in (0, 1), "too many limiters"

  # First, build the query
  rel_cls = model.FullRelationship
  order = (lambda p: p) if ascending else (lambda p: -p)
  query = rel_cls.query(ancestor=UKey(uid))
  if cache_time is not None:
    query = query.filter(ndb.OR(
        rel_cls.last_incoming > cache_time,
        rel_cls.last_sent_rose > cache_time,
        rel_cls.last_sent_message > cache_time))

  # Apply the filters
  if new:
    query = query.filter(
        ndb.OR(rel_cls.new_roses > 0, rel_cls.new_messages > 0))
  if saved_only:
    query = query.filter(rel_cls.saved == True)
  query = query.filter(rel_cls.blocked == blocked_only)

  # Apply the sort order, and filter out anything for which the sort order
  # property is null.
  if sent_rose_only:
    sort_prop = rel_cls.last_sent_rose
  elif received_rose_only:
    sort_prop = rel_cls.last_received_rose
  elif sent_message_only:
    sort_prop = rel_cls.last_sent_message
  elif received_message_only:
    sort_prop = rel_cls.last_received_message
  elif visited_only:
    rel_cls.last_visited
  elif visited_by_only:
    rel_cls.last_visited_by
  else:
    sort_prop = rel_cls.last_incoming
  query = query.filter(sort_prop > model.NEVER).order(order(sort_prop))

  # Convert to dictionaries and add user names
  full_rels = query.fetch(limit, offset=offset)
  inbox = []
  for rel in full_rels:
    uid = rel.key.id()
    user = GetUser(uid)
    rel_dict = rel.to_dict()
    del rel_dict["class_"]
    rel_dict["uid"] = uid
    rel_dict["name"] = user.name
    inbox.append(rel_dict)

  return inbox
