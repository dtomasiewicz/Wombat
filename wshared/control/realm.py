from socket import inet_aton, inet_ntoa
from struct import pack

from wproto.message import Message
from wproto.packutils import prepack, recvnstr, recvdata, recvbytes

from wshared.control.game import Action, Response


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


class GetInstance(Action):
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


class AvatarNoExists(Response):
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
    return AvatarNoExists(recvnstr(sock))


class AvatarInUse(Response):
  pass


class InstanceInfo(Response):
  """
  IDENTIFIER   TYPE           TRANSPORT PACKING
  addr         str            4s (from inet_aton)
    dotted-quad address of instance server
  port         int            H
    integral port number of instance server
  unitid       int            I
    avatar's unit id on instance server
  unitkey      bytes          32s
    avatar's randomized auth key on instance server
  """
  def __init__(self, addr, port, unitid, unitkey):
    self.addr = addr
    self.port = port
    self.unitid = unitid
    self.unitkey = unitkey
  
  def pack(self):
    return prepack(inet_aton(self.addr), ('H', self.port),
                   ('I', self.unitid), self.unitkey)
  
  def unpack(sock):
    return InstanceInfo(inet_ntoa(recvbytes(sock, 4)), recvdata(sock, 'H'),
                        recvdata(sock, 'I'), recvbytes(sock, 32))


REALM_ACTION = {
  100: SelectAvatar,
  101: QuitAvatar,
  102: SendMessage
}


REALM_RESPONSE = {
  100: AvatarNoExists,
  101: AvatarInUse
}
