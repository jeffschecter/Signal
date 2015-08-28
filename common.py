"""Library of common functions."""

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
