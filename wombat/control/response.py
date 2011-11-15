from wombat.message import Message

# generic control action (sends a UTF-8 string)
class Response(Message):
  SUCCESS = False
    
class Success(Response):
  SUCCESS = True

class InvalidAction(Response):
  pass

class InvalidNotifyKey(Response):
  pass

class CharNoExists(Response):
  SIMPLE = False
  
  def __init__(self, char):
    self.char = char
    
  def pack(self):
    cb = bytes(self.char, self.STR_ENC)
    cl = len(cb)
    return ('H{0}s'.format(cl), cl, cb)
  
  def unpack(stream):
    return CharNoExists(stream.recvstring(stream.recvshort(), __class__.STR_ENC))
