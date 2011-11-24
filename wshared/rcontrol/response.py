from wproto.packutils import prepack, recvstring

from wshared.control.response import Response


class AvatarNoExists(Response):  
  def __init__(self, avatar):
    self.avatar = avatar
  def pack(self):
    return prepack(self.avatar)
  def unpack(sock):
    return AvatarNoExists(recvstring(sock))


class AvatarInUse(Response):
  pass
