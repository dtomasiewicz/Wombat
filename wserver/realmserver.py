from wshared.control.realm import REALM_ACTION, REALM_RESPONSE
from wshared.notify.realm import REALM_NOTIFY

from wserver.gameserver import GameServer
from wserver.react.realm import REALM_REACTION
from wserver.avatar import Avatar


class RealmServer(GameServer):
  
  
  def __init__(self, data):
    super().__init__(REALM_ACTION, REALM_RESPONSE, REALM_NOTIFY,
                     REALM_REACTION)
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

