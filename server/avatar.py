from wombat.control.action import *
from wombat.control.response import *

class Avatar:
  """ Avatars are player-controlled Units. """
  def __init__(self, name):
    self.name = name
    self.client = None
  
  def setclient(self, client):
    self.client = client
  
  def act(self, action):
    
    if isinstance(action, SendMessage):
      if self.client.server.message(action.avatar, self.name, action.message):
        return Success()
      else:
        return AvatarNoExists(action.avatar)
    else:
      return InvalidAction()
