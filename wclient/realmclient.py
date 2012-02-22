from wshared.protocol import mapping
from wproto.message import Message
from wclient.gameclient import GameClient


class RealmClient(GameClient):
  
  
  def __init__(self):
    super().__init__(mapping('realm_action'), mapping('realm_response'),
                     mapping('realm_notify'))
  
  
  def debug(self, msg):
    super().debug("RLM: "+msg)
  
    
  def ndebug(self, n):
    if n.istype('RecvMessage'):
      self.debug("[{0}]: {1}".format(n.avatar, n.message))
    else:
      super().ndebug(n)
  
  
  def selectavatar(self, avatar, handler):
    self.control.send(Message('SelectAvatar', avatar=avatar))
    self._handlers.append(handler)
  
  
  def quitavatar(self, handler):
    self.control.send(Message('QuitAvatar'))
    self._handlers.append(handler)
  
  
  def sendmessage(self, avatar, message, handler):
    self.control.send(Message('SendMessage', avatar=avatar, message=message))
    self._handlers.append(handler)
  
  
  def getworldinfo(self, handler):
    self.control.send(Message('GetWorldInfo'))
    self._handlers.append(handler)

