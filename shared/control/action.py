from wombat.message import Message
from wombat.packutils import prepack, recvstring, recvintus

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
