from wombat.message import Message
from wombat.packutils import recvintus, recvstring, prepack

class Notification(Message):
  pass

class NotifyKey(Notification):
  SIMPLE = False
  
  def __init__(self, key):
    self.key = key
  
  def pack(self):
    return prepack(self.key)
  
  def unpack(sock):
    return NotifyKey(recvintus(sock))

# Type(bytelen)  Data
# short          sender's name byte-length (c)
# string(c)      sender's name
# short          message byte-length (m)
# string(m)      message
class RecvMessage(Notification):
  SIMPLE = False
  
  def __init__(self, avatar, message):
    self.avatar = avatar
    self.message = message

  def pack(self):
    return prepack(self.avatar, self.message)
  
  def unpack(sock):
    return RecvMessage(recvstring(sock), recvstring(sock))
