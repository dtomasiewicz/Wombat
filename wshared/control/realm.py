from wproto.message import Message
from wproto.packutils import prepack, recvstring, recvintus

from wshared.control.game import Action, Response


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


class AvatarNoExists(Response):  
  def __init__(self, avatar):
    self.avatar = avatar
  def pack(self):
    return prepack(self.avatar)
  def unpack(sock):
    return AvatarNoExists(recvstring(sock))


class AvatarInUse(Response):
  pass


REALM_ACTION = {
  100: AvatarSelect,
  101: AvatarQuit,
  102: SendMessage
}


REALM_RESPONSE = {
  100: AvatarNoExists,
  101: AvatarInUse
}
