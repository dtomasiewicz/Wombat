from wproto.message import Message
from wproto.packutils import recvintus, recvstring, prepack


class Notification(Message):
  pass

class NotifyKey(Notification):
  def __init__(self, key):
    self.key = key
  def pack(self):
    return prepack(self.key)
  def unpack(sock):
    return NotifyKey(recvintus(sock))
