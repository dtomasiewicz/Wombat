from wshared.protocol import mapping
from wclient.gameclient import GameClient


class WorldClient(GameClient):
  
  
  def __init__(self):
    super().__init__(mapping('world_action'), mapping('world_response'),
                     mapping('world_notify'))
    self.unit = None
  
  
  def selectunit(self, unitid, unitkey):
    with self.controllock:
      res = self.control.sendrecv(Message('SelectUnit', unitid=unitid, unitkey=unitkey))
      if res.isType('Success'):
        self.unit = unitid
        self.debug("Unit selected: {0}".format(unitid))
      elif res.isType('UnitInUse'):
        self.debug("Unit in use: {0}.".format(unitid))
      else:
        self.debug("Failed to select unit: {0}".format(unitid))
      return res

