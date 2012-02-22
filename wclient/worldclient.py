from wproto.message import Message
from wshared.protocol import mapping
from wclient.gameclient import GameClient


class WorldClient(GameClient):
  
  
  def __init__(self):
    super().__init__(mapping('world_action'), mapping('world_response'),
                     mapping('world_notify'))
  
  
  def selectunit(self, id, key, handler=None):
    return self.act(Message('SelectUnit', id=id, key=key), handler)
  
  
  def quitunit(self, handler=None):
    return self.act(Message('QuitUnit'), handler)
