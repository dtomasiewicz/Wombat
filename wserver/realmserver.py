from wshared.protocol import mapping

from wserver.gameserver import GameServer
from wserver.react.realm import REALM_REACTION
from wserver.avatar import Avatar


class RealmServer(GameServer):
  
  
  def __init__(self, data):
    super().__init__(mapping('realm_action'), mapping('realm_response'),
                     mapping('realm_notify'), REALM_REACTION)
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
  
  
  def worldlookup(self, worldid):
    """
    Determines the address and port of a world server given a world id. This 
    method is a stub, which will obviously need to do more later-- perhaps
    query a central master world server.
    """
    return (self.host, self.cport+2, self.nport+2)
