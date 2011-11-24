from wshared.rcontrol.mapping import ACTION_MAPPING, RESPONSE_MAPPING
from wshared.rnotify.mapping import NOTIFY_MAPPING

from wserver.gameserver import GameServer
from wserver.reactor import Reactor
from wserver.rreact.mapping import REACTION_MAPPING
from wserver.avatar import Avatar


class RealmServer(GameServer):
  
  
  def __init__(self, data):
    super().__init__(ACTION_MAPPING, RESPONSE_MAPPING, NOTIFY_MAPPING,
                     REACTION_MAPPING)
    self._data = data
    self._avatars = {}
  
  
  def removeclient(self, client):
    super().removeclient(client)
    if client.avatar:
      client.avatar.client = None
      client.avatar = None
  
  
  def avatar(self, name):
    """ Returns the avatar with the given name, if it exists. """
    if not name in self._avatars:
      a = Avatar.first(self._data, name=name)
      if a:
        self._avatars[name] = a
    return self._avatars.get(name, None)

