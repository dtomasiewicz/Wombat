from wproto.message import Message
from wproto.packutils import prepack, recvdata, recvbytes

from wshared.control.game import Action, Response, Success


class SelectUnit(Action):
  """
  IDENTIFIER   TYPE           TRANSPORT PACKING
  unitid       int            I
    id of unit
  key          bytes          32s
    unit's selection key
  """
  def __init__(self, unitid, key):
    self.unitid = unitid
    self.key = key
  def pack(self):
    return prepack(('I', self.unitid), self.key)
  def unpack(sock):
    return SelectUnit(recvdata(sock, 'I'), recvbytes(sock, 32))


class InvalidUnit(Response):
  """
  IDENTIFIER   TYPE           TRANSPORT PACKING
  unitid       str            I
    id of unit
  """
  def __init__(self, unitid):
    self.unitid = unitid
  def pack(self):
    return prepack(('I', self.unitid))
  def unpack(sock):
    return InvalidUnit(recvdata(sock, 'I'))


class InvalidKey(Response):
  pass


class UnitInUse(Response):
  pass
  

WORLD_ACTION = {
  100: SelectUnit
}


WORLD_RESPONSE = {
  100: InvalidUnit,
  101: InvalidKey,
  102: UnitInUse
}
