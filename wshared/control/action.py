from wproto.message import Message
from wproto.packutils import prepack, recvstring, recvintus


class Action(Message):
  pass


class ClaimNotify(Action):
  def __init__(self, key):
    self.key = key
  def pack(self):
    return prepack(self.key)
  def unpack(sock):
    return ClaimNotify(recvintus(sock))


class Quit(Action):
  pass
