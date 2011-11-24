from wproto.message import Message
from wproto.packutils import prepack, recvstring, recvintus

from wshared.control.action import Action


class AvatarSelect(Action):
  def __init__(self, avatar):
    self.avatar = avatar
  def pack(self):
    return prepack(self.avatar)
  def unpack(sock):
    return AvatarSelect(recvstring(sock))


class AvatarQuit(Action):
  pass


class SendMessage(Action):
  def __init__(self, avatar, message):
    self.avatar = avatar
    self.message = message
  def pack(self):
    return prepack(self.avatar, self.message)
  def unpack(sock):
    return SendMessage(recvstring(sock), recvstring(sock))
