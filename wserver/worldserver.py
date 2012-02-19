from wshared.protocol import mapping

from wserver.gameserver import GameServer
from wserver.react.world import WORLD_REACTION
from wserver.unit import Unit


class WorldServer(GameServer):
  
  
  def __init__(self, data):
    super().__init__(mapping('world_action'), mapping('world_response'),
                     mapping('world_notify'), WORLD_REACTION)
    self._data = data
    self._units = {}
  
  
  def removeclient(self, client):
    super().removeclient(client)
    if client.unit:
      client.unit.client = None
      client.unit = None
  
  
  def unit(self, id):
    """ Returns the unit with the given ID, if it exists. """
    if not id in self._units:
      u = Unit.first(self._data, id=id)
      if u:
        self._units[id] = u
    return self._units.get(id, None)
  
