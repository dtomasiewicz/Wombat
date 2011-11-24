from wshared.control.response import *
from wshared.notify.notification import *


class Reaction:
  """ An event that handles a client action. """
  READONLY = None
  
  def __init__(self, client, action):
    self.client = client
    self.action = action
    
  def process(self):
    res = self.react()
    if res:
      self.client.debug("{0} => {1}".format(self.action, res))
      self.client.control.send(res)
      #if len(select([client], [], [], 0)[0]) == 1:
      #  self._clientdata(client)
      self.client.realm.idleclient(self.client)
    else:
      self.client.realm.removeclient(self.client)
  
  def react(self):
    raise Exception("Must extend Reaction.react in subclasses.")


class RQuit(Reaction):
  READONLY = False
  def react(self):
    if self.client.avatar:
      return InvalidAction()
    else:
      self.client.control.send(Success())
      return False

    
class RClaimNotify(Reaction):
  READONLY = False
  def react(self):
    self.client.notify = self.client.realm.claimnotify(self.action.key)
    return Success() if self.client.notify else InvalidNotifyKey()

