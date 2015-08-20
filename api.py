"""Initializes application with routes and endpoints."""

import webapp2

from handlers import account
from handlers import garden
from handlers import history
from handlers import message
from handlers import profile


HANDLER_MODULES = (
  account,
  garden,
  history,
  message,
  profile,
  )


ROUTES = ()
for module in HANDLER_MODULES:
  ROUTES += module.ROUTES


API = webapp2.WSGIApplication(ROUTES, debug=True)
