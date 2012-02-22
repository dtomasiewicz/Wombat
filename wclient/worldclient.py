from wproto.message import Message
from wshared.protocol import mapping
from wclient.gameclient import GameClient


class WorldClient(GameClient):
  
  
  def __init__(self):
    super().__init__(mapping('world_action'), mapping('world_response'),
                     mapping('world_notify'))
  
  def debug(self, msg):
    super().debug("WLD: "+msg)
  
  
  def selectunit(self, id, key, handler):
    self.control.send(Message('SelectUnit', id=id, key=key))
    self._handlers.append(handler)
  
  
  def quitunit(self, handler):
    self.control.send(Message('QuitUnit'))
    self._handlers.append(handler)
