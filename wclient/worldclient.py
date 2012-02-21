from wproto.message import Message
from wshared.protocol import mapping
from wclient.gameclient import GameClient


class WorldClient(GameClient):
  
  
  def __init__(self):
    super().__init__(mapping('world_action'), mapping('world_response'),
                     mapping('world_notify'))
    self.unit = None
  
  def debug(self, msg):
    super().debug("WLD: "+msg)
  
  def selectunit(self, id, key):
    with self.controllock:
      res = self.control.sendrecv(Message('SelectUnit', id=id, key=key))
      if res.istype('Success'):
        self.unit = id
        self.debug("Unit selected: {0}".format(id))
      elif res.istype('UnitInUse'):
        self.debug("Unit in use: {0}.".format(id))
      else:
        self.debug("Failed to select unit: {0}".format(id))
      return res

