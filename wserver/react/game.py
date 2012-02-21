from wserver.reactor import Reaction
from wproto.message import Message


class RQuit(Reaction):
  def react(self):
    if self.client.avatar or self.client.unit:
      return Message('InvalidAction')
    else:
      self.disconnect = True
      return True

    
class RClaimNotify(Reaction):
  def react(self):
    self.client.notify = self.client.realm.claimnotify(self.action.key)
    return True if self.client.notify else Message('InvalidNotifyKey')


GAME_REACTION = {
  'Quit': RQuit,
  'ClaimNotify': RClaimNotify
}

