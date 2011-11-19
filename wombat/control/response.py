from wombat.message import Message
from wombat.packutils import recvstring

# generic control action (sends a UTF-8 string)
class Response(Message):
  SUCCESS = False
    
class Success(Response):
  SUCCESS = True

class InvalidAction(Response):
  pass

class InvalidNotifyKey(Response):
  pass

class AvatarNoExists(Response):
  SIMPLE = False
  
  def __init__(self, avatar):
    self.avatar = avatar
    
  def pack(self):
    return prepack(self.avatar)
  
  def unpack(sock):
    return Avatar(recvstring(sock))
