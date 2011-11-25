from wproto.message import Message
from wproto.packutils import recvintus, recvstring, prepack

from wshared.notify.game import Notification


class RecvMessage(Notification):
  SIMPLE = False
  
  def __init__(self, avatar, message):
    self.avatar = avatar
    self.message = message

  def pack(self):
    return prepack(self.avatar, self.message)
  
  def unpack(sock):
    return RecvMessage(recvstring(sock), recvstring(sock))


REALM_NOTIFY = {
  100: RecvMessage
}
