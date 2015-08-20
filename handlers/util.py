"""Utilities for defining endpoints."""

import json
import logging
import webapp2


class RequestHandler(webapp2.RequestHandler):

  def __init__(self, *args, **kwargs):
    webapp2.RequestHandler.__init__(self, *args, **kwargs)

  def get(self):
    self.Respond()

  def post(self):
    self.Respond()

  def Set(self, k, v):
    self.RESPONSE_DATA[k] = v

  def Respond(self):
    self.response.headers['Content-Type'] = 'text/json'
    self.RESPONSE_DATA = {}
    try:
      query = json.loads(self.request.params.get('data'))
      self.context = query.get("context", {})
      self.args = query.get("args", {})
      self.Handle()
      self.RESPONSE_DATA = json.dumps(self.RESPONSE_DATA)
    except Exception as e:
      logging.exception(e)
      self.RESPONSE_DATA = json.dumps({
        "error": type(e).__name__,
        "error_string": str(e)})
    finally:
      self.response.write(self.RESPONSE_DATA)


def TODO():
  raise NotImplementedError("This endpoint has not been implemented.")
