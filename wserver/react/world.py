from wproto.message import Message
from wserver.reactor import Reaction

class RSelectUnit(Reaction):
  READONLY = False
  def react(self):
    if self.client.unit:
      return Message('InvalidAction')
    else:
      u = self.client.realm.unit(self.action.get('unitid'))
      if not u:
        return Message('InvalidUnit', unitid=self.action.get('unitid'))
      elif u.client:
        return Message('UnitInUse')
      elif u.key != self.action.key:
        return Message('InvalidKey')
      else:
        self.client.unit = u
        u.client = self.client
        return Message('Success')


WORLD_REACTION = {
  'SelectUnit': RSelectUnit
}
