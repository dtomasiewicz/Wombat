from wserver.reactor import Reaction
from wproto.message import Message


class RQuit(Reaction):
  READONLY = False
  def react(self):
    if self.client.avatar or self.client.unit:
      return Message('InvalidAction')
    else:
      self.client.control.send(Message('Success'))
      return False

    
class RClaimNotify(Reaction):
  READONLY = False
  def react(self):
    self.client.notify = self.client.realm.claimnotify(self.action.get('key'))
    return Message('Success') if self.client.notify else Message('InvalidNotifyKey')


GAME_REACTION = {
  'Quit': RQuit,
  'ClaimNotify': RClaimNotify
}

