from wproto.message import Message
from wproto.packutils import prepack, recvbytes


class Notification(Message):
  pass


class NotifyKey(Notification):
  """
  IDENTIFIER   TYPE           TRANSPORT PACKING
  key          bytes          32s
    notify stream's randomized claim key
  """
  def __init__(self, key):
    self.key = key
  def pack(self):
    return prepack(self.key)
  def unpack(sock):
    return NotifyKey(recvbytes(sock, 32))


GAME_NOTIFY = {
  1: NotifyKey
}
