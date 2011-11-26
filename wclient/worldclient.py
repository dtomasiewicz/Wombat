from wshared.control.world import *
from wshared.notify.world import *

from wclient.gameclient import GameClient


class WorldClient(GameClient):
  
  
  def __init__(self):
    super().__init__(WORLD_ACTION, WORLD_RESPONSE, WORLD_NOTIFY)
    self.unit = None
  
  
  def selectunit(self, unitid, unitkey):
    with self.controllock:
      res = self.control.sendrecv(SelectUnit(unitid, unitkey))
      if res.SUCCESS:
        self.unit = unitid
        self.debug("Unit selected: {0}".format(unitid))
      elif isinstance(res, UnitInUse):
        self.debug("Unit in use: {0}.".format(unitid))
      else:
        self.debug("Failed to select unit: {0}".format(unitid))
      return res

