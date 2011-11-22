from wombat.control.action import *
from wombat.control.response import *
from wombat.notify.notification import *

from data.model import Model

class Avatar(Model):
  """ Avatars are player-controlled Units. """
  SCHEMA = ('id', 'name')
  TABLE = 'avatar'
  
  def _init(self):
    self.client = None
  
  def act(self, action):
    
    if isinstance(action, SendMessage):
      avatar = self.client.server.avatar(action.avatar)
      success = False
      if avatar:
        with avatar:
          success = avatar.sendmessage(self.name, action.message)
      return Success() if success else AvatarNoExists(action.avatar)
    else:
      return InvalidAction()

  def sendmessage(self, from_, message):
    """ Send a message to this avatar. Lock first. """
    if self.client:
      with self.client:
        if self.client.notify:
          self.client.notify.send(RecvMessage(from_, message))
          return True
    return False
