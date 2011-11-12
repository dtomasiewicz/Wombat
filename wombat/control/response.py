from ..message import Message

# generic control action (sends a UTF-8 string)
class Response(Message):
  SUCCESS = False
    
class Success(Response):
  SUCCESS = True

class InvalidAction(Response):
  pass

# Type(bytelen)  Data
# short          client ID
class Identity(Success):
  SIMPLE = False
  
  def __init__(self, identity):
    self.identity = identity
  
  def pack(self):
    return ('H', self.identity)
  
  def unpack(stream):
    return Identity(stream.recvshort())

class InvalidIdentity(Response):
  pass

class RemapNotify(Success):
  pass
