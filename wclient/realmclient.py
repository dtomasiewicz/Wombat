from wshared.control.realm import *
from wshared.notify.realm import *

from wclient.gameclient import GameClient


class RealmClient(GameClient):
  
  
  def __init__(self):
    super().__init__(REALM_ACTION, REALM_RESPONSE, REALM_NOTIFY)
    self.avatar = None
    
    
  def ndebug(self, n):
    if isinstance(n, RecvMessage):
      self.debug("[{0}]: {1}".format(n.avatar, n.message))
    else:
      super().ndebug(n)
  
  
  def selectavatar(self, avatar):
    with self.controllock:
      res = self.control.sendrecv(SelectAvatar(avatar))
      if res.SUCCESS:
        self.avatar = avatar
        self.debug("Avatar selected: {0}".format(avatar))
      elif isinstance(res, AvatarInUse):
        self.debug("Avatar in use: {0}.".format(avatar))
      else:
        self.debug("Failed to select avatar: {0}".format(avatar))
      return res
  
  
  def quitavatar(self):
    with self.controllock:
      res = self.control.sendrecv(QuitAvatar())
      if res.SUCCESS:
        self.avatar = None
        self.debug("Avatar quit success.")
      else:
        self.debug("Avatar quit failure.")
      return res
  
  
  def sendmessage(self, avatar, message):
    with self.controllock:
      res = self.control.sendrecv(SendMessage(avatar, message))
      if res.SUCCESS:
        self.debug("Message sent.")
      elif isinstance(res, InvalidAvatar):
        self.debug("Avatar does not exist: {0}".format(res.avatar))
      else:
        self.debug("Failed to send message.")
      return res
  
  
  def getworldinfo(self):
    with self.controllock:
      return self.control.sendrecv(GetWorldInfo())

