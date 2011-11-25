from wshared.control.game import *
from wshared.notify.game import *

from wserver.reactor import Reaction


class RQuit(Reaction):
  READONLY = False
  def react(self):
    if self.client.avatar:
      return InvalidAction()
    else:
      self.client.control.send(Success())
      return False

    
class RClaimNotify(Reaction):
  READONLY = False
  def react(self):
    self.client.notify = self.client.realm.claimnotify(self.action.key)
    return Success() if self.client.notify else InvalidNotifyKey()


GAME_REACTION = {
  Quit: RQuit,
  ClaimNotify: RClaimNotify
}

