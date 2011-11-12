from struct import pack, unpack

# generic control action (does not carry any data; just the op code)
class Message:
  STR_ENC = 'UTF-8'
  
  # if simple is False in subclass, subclass must define its own pack and
  # unpack (static) methods
  SIMPLE = True

  def istype(self, typ):
    return self.__class__ == typ
