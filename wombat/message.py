from struct import pack, unpack

# generic control action (sends a UTF-8 string)
class Message:
  STR_ENC = 'UTF-8'
  
  # if simple is False in subclass, subclass must define its own pack and
  # unpack (static) methods
  SIMPLE = True

  def istype(self, typ):
    return self.__class__ == typ