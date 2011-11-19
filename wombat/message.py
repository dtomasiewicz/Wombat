class Message:
  """ Generic stream message. Does not carry any data. """
  
  # if simple is False in subclass, subclass must define its own pack and
  # unpack methods
  SIMPLE = True

class CodeError(Exception):
  def __init__(self, code):
    self.code = code
