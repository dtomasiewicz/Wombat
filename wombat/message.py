from struct import pack, unpack

class Message:
  """ Generic stream message. Does not carry any data. """
  STR_ENC = 'UTF-8'
  
  # if simple is False in subclass, subclass must define its own pack and
  # unpack(static) methods
  SIMPLE = True
