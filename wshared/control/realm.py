from socket import inet_aton, inet_ntoa

from wproto.message import Message
from wproto.packutils import prepack, recvnstr, recvdata, recvbytes

from wshared.control.game import Action, Response, Success


class SelectAvatar(Action):
  """
  IDENTIFIER   TYPE           TRANSPORT PACKING
  avatar       str            H{n}s
    name of avatar
  """
  def __init__(self, avatar):
    self.avatar = avatar
  def pack(self):
    return prepack(self.avatar)
  def unpack(sock):
    return SelectAvatar(recvnstr(sock))


class QuitAvatar(Action):
  pass


class GetWorldInfo(Action):
  """
  Retrieves information for connecting to the world server of the currently
  selected avatar.
  """
  pass


class SendMessage(Action):
  """
  IDENTIFIER   TYPE           TRANSPORT PACKING
  avatar       str            H{n}s
    name of receiving avatar
  message      str            H{n}s
    message content
  """
  def __init__(self, avatar, message):
    self.avatar = avatar
    self.message = message
  def pack(self):
    return prepack(self.avatar, self.message)
  def unpack(sock):
    return SendMessage(recvnstr(sock), recvnstr(sock))


class InvalidAvatar(Response):
  """
  IDENTIFIER   TYPE           TRANSPORT PACKING
  avatar       str            H{n}s
    name of avatar
  """
  def __init__(self, avatar):
    self.avatar = avatar
  def pack(self):
    return prepack(self.avatar)
  def unpack(sock):
    return InvalidAvatar(recvnstr(sock))


class AvatarInUse(Response):
  pass


class WorldInfo(Success):
  """
  IDENTIFIER   TYPE           TRANSPORT PACKING
  addr         str            4s (from inet_aton)
    dotted-quad address of world server
  cport        int            H
    integral control port number of world server
  nport        int            H
    integral notify port number of world server
  worldid      int            I
    id of world on world server
  unitid       int            I
    avatar's unit id on world server
  unitkey      bytes          32s
    avatar's randomized auth key on world server
  """
  def __init__(self, addr, cport, nport, worldid, unitid, unitkey):
    self.addr = addr
    self.cport = cport
    self.nport = nport
    self.worldid = worldid
    self.unitid = unitid
    self.unitkey = unitkey
  
  def pack(self):
    return prepack(inet_aton(self.addr), ('H', self.cport), ('H', self.nport),
                   ('I', self.worldid), ('I', self.unitid), self.unitkey)
  
  def unpack(sock):
    return WorldInfo(
        inet_ntoa(recvbytes(sock, 4)), recvdata(sock, 'H'), recvdata(sock, 'H'),
        recvdata(sock, 'I'), recvdata(sock, 'I'), recvbytes(sock, 32))


REALM_ACTION = {
  100: SelectAvatar,
  101: QuitAvatar,
  102: GetWorldInfo,
  103: SendMessage
}


REALM_RESPONSE = {
  100: InvalidAvatar,
  101: AvatarInUse,
  102: WorldInfo
}
