"""Library of common functions."""

import base64
import datetime


EPOCH = datetime.datetime.utcfromtimestamp(0)


def Milis(dt):
  """Converts a datetime to miliseconds since epoch.

  Args:
    dt: (datetime.datetime) The datetime to convert.

  Returns:
    (int) Miliseconds since epoch.
  """
  return int((dt - EPOCH).total_seconds() * 1000)


def JsonEncoder(obj):
  """Handles encoding to JSON of objects that python usually wigs out on.

  Args:
    obj: (*) The object to encode.

  Returns:
    (string) A serialized version of the object.
  """
  # For date, time, and datetime, convert to isoformat string
  if hasattr(obj, 'isoformat'):
    return obj.isoformat()
  else:
    raise TypeError(
        "Object of type {t} with value of {v} is not JSON serializable".format(
            t=type(obj), v=repr(obj)))


def Decode(b64):
  """Decodes base64 strings.

  We use a url-safe encoding that utilizes "-" and "_" instead of the default
  "+" and "/" characters, and handle any padding issues without raising errors.

  Args:
    b64: (str) The encoded string.

  Returns:
    (str) The decoded string.
  """
  missing_padding = 4 - len(b64) % 4
  if missing_padding:
    b64 += b'='* missing_padding
  return base64.b64decode(str(b64), "-_")


def Encode(string):
  """Encodes a string in url-safe base64.

  Args:
    string: (str) The string to encode.

  Returns:
    (str) The safely encoded string.
  """
  return base64.b64encode(string, "-_")