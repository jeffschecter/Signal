"""Defines the data model for interacting with Datastore."""

from google.appengine.ext import ndb
from google.appengine.ext.ndb import polymodel


class GeoCoordProperty(ndb.FloatProperty):
  """Property for latitude and longitude values."""

  # pylint: disable=no-self-use
  def _validate(self, value):
    """Validates latitude and longitude."""
    msg = "Latitude and Longitude must be between -180 and 180."
    assert value >= -180.0 and value <= 180.0, msg


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


class IntroFile(ndb.Model):
  """A user's audio intro.

  Ancestor: (User) The user
  Name: 1
  """
  blob = ndb.BlobProperty(required=True)


class ImageFile(ndb.Model):
  """A user's chat image.

  Ancestor: (User) The user
  Name: 1
  """
  blob = ndb.BlobProperty(required=True)


class MatchParameters(ndb.Model):
  """Defines user properties indexed for finding matches.

  Ancestor: (User) The user
  Name: 1
  """
  # 0=male, 1=female, 2=other
  gender = ndb.IntegerProperty(choices=[0, 1, 2])
  # 0=gay, 1=straight, 2=bi, 3=other
  sexuality = ndb.IntegerProperty(choices=[0, 1, 2, 3])
  birthday = ndb.DateTimeProperty()
  last_activity = ndb.DateTimeProperty()
  latitude = GeoCoordProperty()
  longitude = GeoCoordProperty()
  active = ndb.BooleanProperty(default=True)


class SearchSettings(ndb.Model):
  """Defines the types of partners a user wants to match with.

  Ancestor: (User) The user
  Name: 1
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
  Name: 1
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
  Name: 1, 1, or 2 (each user has 3 roses)
  """
  bloomed = ndb.DateTimeProperty(required=True)  # In the future when unbloomed
  planted = ndb.DateTimeProperty(required=True)


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
  blocked = ndb.BooleanProperty(default=False)
  saved = ndb.BooleanProperty(default=False)
  new_roses = ndb.IntegerProperty(default=0)
  new_messages = ndb.IntegerProperty(default=0)
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
  new = ndb.BooleanProperty(required=True, default=True)
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


class MessageFile(ndb.Model):
  """An audio message.

  Ancestor: (User, Relationship) The sender and recipient, respectively.
  Name: (int) Send timestamp, in miliseconds since epoch.
  """
  blob = ndb.BlobProperty(required=True)
