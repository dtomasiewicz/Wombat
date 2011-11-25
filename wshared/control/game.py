from wproto.message import Message
from wproto.packutils import prepack, recvbytes


class Action(Message):
  pass


class ClaimNotify(Action):
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
    return ClaimNotify(recvbytes(sock, 32))


class Quit(Action):
  pass


class Response(Message):
  SUCCESS = False

    
class Success(Response):
  SUCCESS = True


class InvalidAction(Response):
  pass


class InvalidNotifyKey(Response):
  pass


GAME_ACTION = {
  0: Quit,
  1: ClaimNotify
}


GAME_RESPONSE = {
  0: Success,
  1: InvalidAction,
  2: InvalidNotifyKey
}
