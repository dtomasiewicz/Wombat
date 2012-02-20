from wshared.protocol import mapping
from wproto.message import Message
from wclient.gameclient import GameClient


class RealmClient(GameClient):
  
  
  def __init__(self):
    super().__init__(mapping('realm_action'), mapping('realm_response'),
                     mapping('realm_notify'))
    self.avatar = None
    
  def ndebug(self, n):
    if n.alias == 'RecvMessage':
      self.debug("[{0}]: {1}".format(n.get('avatar'), n.get('message')))
    else:
      super().ndebug(n)
  
  
  def selectavatar(self, avatar):
    with self.controllock:
      res = self.control.sendrecv(Message('SelectAvatar', avatar=avatar))
      if res.alias == 'Success':
        self.avatar = avatar
        self.debug("Avatar selected: {0}".format(avatar))
      elif res.alias == 'AvatarInUse':
        self.debug("Avatar in use: {0}.".format(avatar))
      else:
        self.debug("Failed to select avatar: {0}".format(avatar))
      return res
  
  
  def quitavatar(self):
    with self.controllock:
      res = self.control.sendrecv(Message('QuitAvatar'))
      if res.alias == 'Success':
        self.avatar = None
        self.debug("Avatar quit success.")
      else:
        self.debug("Avatar quit failure.")
      return res
  
  
  def sendmessage(self, avatar, message):
    with self.controllock:
      res = self.control.sendrecv(Message('SendMessage', avatar=avatar, message=message))
      if res.alias == 'Success':
        self.debug("Message sent.")
      elif res.alias == 'InvalidAvatar':
        self.debug("Avatar does not exist: {0}".format(res.get('avatar')))
      else:
        self.debug("Failed to send message.")
      return res
  
  
  def getworldinfo(self):
    with self.controllock:
      return self.control.sendrecv(Message('GetWorldInfo'))

