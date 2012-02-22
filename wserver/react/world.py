from wproto.message import Message
from wserver.reactor import Reaction

class RSelectUnit(Reaction):
  def react(self):
    if self.client.unit:
      return Message('InvalidAction')
    else:
      u = self.client.realm.unit(self.action.id)
      if not u:
        return Message('InvalidUnit', id=self.action.id)
      elif u.client:
        return Message('UnitInUse')
      elif u.key != self.action.key:
        return Message('InvalidKey')
      else:
        self.client.unit = u
        u.client = self.client
        return True


class RQuitUnit(Reaction):
  def react(self):
    if self.client.unit:
      self.client.unit.client = None
      self.client.unit = None
      return True
    else:
      return Message('InvalidAction')


WORLD_REACTION = {
  'SelectUnit': RSelectUnit,
  'QuitUnit': RQuitUnit
}
