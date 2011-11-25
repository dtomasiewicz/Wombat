from wproto.message import Message
from wproto.packutils import prepack, recvnstr

from wshared.notify.game import Notification


class RecvMessage(Notification):
  """
  IDENTIFIER   TYPE           TRANSPORT PACKING
  avatar       str            H{n}s
    name of sending avatar
  message      str            H{n}s
    message content
  """
  SIMPLE = False
  def __init__(self, avatar, message):
    self.avatar = avatar
    self.message = message
  def pack(self):
    return prepack(self.avatar, self.message)
  def unpack(sock):
    return RecvMessage(recvnstr(sock), recvnstr(sock))


REALM_NOTIFY = {
  100: RecvMessage
}
