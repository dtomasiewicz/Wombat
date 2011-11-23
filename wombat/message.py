class Message:
  """ Generic stream message. Does not carry any data. """
  pack = None
  unpack = None
  
  def __str__(self):
    return self.__class__.__name__


class CodeError(Exception):
  def __init__(self, code):
    self.code = code
