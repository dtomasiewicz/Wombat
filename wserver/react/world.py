from wshared.control.world import *
from wshared.control.game import Success, InvalidAction

from wserver.reactor import Reaction


class RSelectUnit(Reaction):
  READONLY = False
  def react(self):
    if self.client.unit:
      return InvalidAction()
    else:
      u = self.client.realm.unit(self.action.unitid)
      if not u:
        return InvalidUnit(self.action.unitid)
      elif u.client:
        return UnitInUse()
      elif u.key != self.action.key:
        return InvalidKey()
      else:
        self.client.unit = u
        u.client = self.client
        return Success()


WORLD_REACTION = {
  SelectUnit: RSelectUnit
}
