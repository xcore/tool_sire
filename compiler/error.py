import sys

class Error(Exception):
  """
  A generic error Exception class.
  """
  pass
#  def __init__(self, value):
#    self.value = value
#
#  def __str__(self):
#    return repr(self.value)

class QuietError(Exception):
    pass

