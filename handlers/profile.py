"""Endpoints for working with profile browsing."""

from google.appengine.ext import ndb
from handlers.lib import ioformat
from handlers.lib import util
from storage import interface
from storage import model


ROUTES = []

# --------------------------------------------------------------------------- #
# Load a match's profile information.                                         #
# --------------------------------------------------------------------------- #

class LoadOutformat(ndb.Model):
  pass


class Load(util.AuthedHandler):

  in_format = ioformat.DesignateUser
  out_format = LoadOutformat

  def Handle(self):
    util.TODO()

ROUTES.append(('/profile/load/*', Load))


# --------------------------------------------------------------------------- #
# Get the next match.                                                         #
# --------------------------------------------------------------------------- #

class Next(util.AuthedHandler):

  in_format = ioformat.Trivial
  out_format = LoadOutformat

  def Handle(self):
    util.TODO()

ROUTES.append(('/profile/next/*', Next))


# --------------------------------------------------------------------------- #
# Retrieve a user's audio introduction.                                       #
# --------------------------------------------------------------------------- #

class Listen(util.AuthedHandler):

  in_format = ioformat.DesignateUser
  out_format = ioformat.AudioOutput

  def Handle(self):
    util.TODO()

ROUTES.append(('/profile/listen/*', Listen))


# --------------------------------------------------------------------------- #
# Save a profile so you can find it again later.                              #
# --------------------------------------------------------------------------- #

class Save(util.AuthedHandler):

  in_format = ioformat.DesignateUser
  out_format = ioformat.Trivial

  def Handle(self):
    util.TODO()

ROUTES.append(('/profile/save/*', Save))


# --------------------------------------------------------------------------- #
# Unsave a profile.                                                           #
# --------------------------------------------------------------------------- #

class Unsave(util.AuthedHandler):

  in_format = ioformat.DesignateUser
  out_format = ioformat.Trivial

  def Handle(self):
    util.TODO()

ROUTES.append(('/profile/unsave/*', Unsave))


# --------------------------------------------------------------------------- #
# Block a user to prevent them from interacting with you.                     #
# --------------------------------------------------------------------------- #

class Block(util.AuthedHandler):

  in_format = ioformat.DesignateUser
  out_format = ioformat.Trivial

  def Handle(self):
    util.TODO()

ROUTES.append(('/profile/block/*', Block))


# --------------------------------------------------------------------------- #
# Unblock a profile.                                                          #
# --------------------------------------------------------------------------- #

class Unblock(util.AuthedHandler):

  in_format = ioformat.DesignateUser
  out_format = ioformat.Trivial

  def Handle(self):
    util.TODO()

ROUTES.append(('/profile/unblock/*', Unblock))
