"""Defines the data model for interacting with Datastore."""

from google.appengine.ext import ndb
from google.appengine.ext.ndb import polymodel


# --------------------------------------------------------------------------- #
# Users are the root of the object tree.                                      #
# --------------------------------------------------------------------------- #

class User(ndb.Model):
  """Defines a user.

  Ancestor: None
  Name: (int) a user id
  """
  name = ndb.StringProperty()
  gender_string = ndb.StringProperty()  # If MatchParameters.gender == 2
  sexuality_string = ndb.StringProperty()  # If MatchParameters.sexuality == 3
  joined = ndb.DateTimeProperty()


class MatchParameters(ndb.Model):
  """Defines user properties indexed for finding matches.

  Ancestor: (User) The user
  Name: 0
  """
  gender = ndb.IntegerProperty()  # 0=male, 1=female, 2=other
  sexuality = ndb.IntegerProperty()  # 0=gay, 1=straight, 2=bi, 3=other
  birthday = ndb.DateTimeProperty()
  last_activity = ndb.DateTimeProperty()
  latitude = ndb.FloatProperty()
  longitude = ndb.FloatProperty()
  country = ndb.StringProperty()
  region = ndb.StringProperty()
  city = ndb.StringProperty()
  active = ndb.BooleanProperty(default=True)


class SearchSettings(ndb.Model):
  """Defines the types of partners a user wants to match with.

  Ancestor: (User) The user
  Name: 0
  """
  radius = ndb.FloatProperty()  # In miles
  min_age = ndb.IntegerProperty()  # In years
  max_age = ndb.IntegerProperty()  # In years
  accept_male_sexualities = ndb.IntegerProperty(repeated=True)
  accept_female_sexualities = ndb.IntegerProperty(repeated=True)
  accept_other_sexualities = ndb.IntegerProperty(repeated=True)


# --------------------------------------------------------------------------- #
# The garden contains roses that a user can send to a prospective match, and  #
# can "water" to make the roses grow faster.                                  #
# --------------------------------------------------------------------------- #

class Garden(ndb.Model):
  """Defines a user's garden.

  Doesn't actually hold any info yet; might contain metadata in the future.

  Ancestor: (User) The user
  Name: 0
  """
  pass


class Watering(ndb.Expando):
  """Defines an instance of a user watering their garden.

  Different types of waterings will have different metadata fields.

  Ancestor: (User, Garden) The user's garden
  Name: Auto
  """
  timestamp = ndb.DateTimeProperty()
  kind = ndb.IntegerProperty()
  bloomed_rose = ndb.IntegerProperty()


class Rose(ndb.Model):
  """Defines a rose growing in the garden.

  Rose has subclasses used in storingrelationships taht differ only in the
  structure of their ancestor path and name.

  Ancestor: (User, Garden) The user's garden
  Name: 0, 1, or 2 (each user has 3 roses)
  """
  bloomed = ndb.DateTimeProperty()  # In the future when unbloomed
  planted = ndb.DateTimeProperty()


# --------------------------------------------------------------------------- #
# Relationships contain all interactions between pairs of users. Data will    #
# always be duplicated across two relationships, for the sender and the       #
# receiver.                                                                   #
# --------------------------------------------------------------------------- #

class Relationship(polymodel.PolyModel):
  """Defines a history of interactions between two users.

  Has two forms, the minimal version for users who have just visited profiles,
  and the "full" form for users who have exchanged communications.

  Ancestor: (User) The "sender" or "agent"
  Name: (int) The "receiver" or "patient"
  """
  last_profile_view = ndb.DateTimeProperty()


class FullRelationship(Relationship):
  """A relationship where users have exchange communications."""
  blocked = ndb.BooleanProperty()
  saved = ndb.BooleanProperty()
  can_see_icon = ndb.BooleanProperty()
  new_roses = ndb.IntegerProperty()
  new_messages = ndb.IntegerProperty()
  last_sent_rose = ndb.DateTimeProperty()
  last_received_rose = ndb.DateTimeProperty()
  last_sent_message = ndb.DateTimeProperty()
  last_received_message = ndb.DateTimeProperty()


class SentRose(Rose):
  """A rose that the agent sent to the patient.

  Ancestor: (User, Relationship) The agent and patient
  Name: (int) Send timestamp, in miliseconds since epoch
  """
  pass


class ReceivedRose(Rose):
  """A rose that the agent received from the patient.

  Ancestor: (User, Relationship) The agent and patient.
  Name: (int) Send timestamp, in miliseconds since epoch
  """
  pass


class Message(ndb.Model):
  """Metadata about a voice message sent from one user to another.

  Message has two subclasses that differ only in the structure of their
  ancestor path and name.

  Name: (int) Send timestamp, in miliseconds since epoch
  """
  length_miliseconds = ndb.IntegerProperty()
  retrieved = ndb.DateTimeProperty(repeated=True)


class SentMessage(Message):
  """A message sent by the agent to the patient.

  Ancestor: (User, Relationship) The sender and recipient, respectively
  """
  pass


class ReceivedMessage(Message):
  """A message received by the agent from the patient.

  Ancestor: (User, Relationship) The recipient and sender, respectively
  """
  pass