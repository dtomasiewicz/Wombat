from ..message import Message

class Notification(Message):
  pass

class NotifyKey(Notification):
  SIMPLE = False
  
  def __init__(self, key):
    self.key = key
  
  def pack(self):
    return ('H', self.key)
  
  def unpack(stream):
    return NotifyKey(stream.recvshort())

class Test(Notification):
  pass
