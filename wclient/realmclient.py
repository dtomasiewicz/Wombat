from wshared.protocol import mapping
from wproto.message import Message
from wclient.gameclient import GameClient


class RealmClient(GameClient):
  
  
  def __init__(self):
    super().__init__(mapping('realm_action'), mapping('realm_response'),
                     mapping('realm_notify'))
  
    
  def ndebug(self, n):
    if n.istype('RecvMessage'):
      self.debug("[{0}]: {1}".format(n.avatar, n.message))
    else:
      super().ndebug(n)
  
  
  def selectavatar(self, avatar, handler=None):
    return self.act(Message('SelectAvatar', avatar=avatar), handler)
  
  
  def quitavatar(self, handler=None):
    return self.act(Message('QuitAvatar'), handler)
  
  
  def sendmessage(self, avatar, message, handler=None):
    return self.act(Message('SendMessage', avatar=avatar, message=message), handler)
  
  
  def getworldinfo(self, handler=None):
    return self.act(Message('GetWorldInfo'), handler)

