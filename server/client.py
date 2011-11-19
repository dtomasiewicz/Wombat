from wombat.control.action import *
from wombat.control.response import *

from combatserver.threads import Lockable

class Client(Lockable):
  """
  Handles all actions that a client machine can perform.
  
  Public threading:
    must be acquired before mutation, invocation, and dependent accesses
  """
  
  def __init__(self, server, control, address):
    super().__init__()
    self.server = server
    self.control = control
    self.address = address
    self.notify = None
    self.user = None
    self.avatar = None
    self.state = self.s_start
  
  def identity(self):
    """ Unique string identifying the client, composed of socket id and IP. """
    return "{0}@{1}".format(id(self), self.address[0])
  
  def debug(self, msg):
    """ Sends client-relevant debugging info to the server. """
    self.server.debug("{0}: {1}".format(self.identity(), msg))
  
  def s_start(self, action):
    """
    Client state after opening the client application or after logging out.
    Valid actions: ClaimNotify, Login, Quit
    """
    if isinstance(action, ClaimNotify):
      self.notify = self.server.claimnotify(action.key)
      if self.notify:
        return Success()
      else:
        return InvalidNotifyKey()
    
    elif isinstance(action, Login):
      self.user = action.user
      self.debug("Logged in as {0}".format(self.user))
      self.state = self.s_loggedin
      return Success()
      
    elif isinstance(action, Quit):
      self.debug("Quit")
      self.state = None
      return Success()
      
    else:
      return InvalidAction()
  
  def s_loggedin(self, action):
    """
    Client state after logging in or deselecting an avatar.
    Valid actions: Logout, AvatarSelect
    """
    
    if isinstance(action, Logout):
      self.debug("Logged out")
      self.user = None
      self.state = self.s_start
      return Success()
        
    elif isinstance(action, AvatarSelect):
      self.avatar = self.server.avatar(action.avatar)
      self.avatar.setclient(self)
      self.debug("Selected {0}".format(self.avatar.name))
      self.state = self.s_avatarselected
      return Success()
      
    else:
      return InvalidAction()
  
  def s_avatarselected(self, action):
    """
    Client state after selecting an avatar.
    """
    
    if isinstance(action, AvatarQuit):
      self.debug("Deselected {0}".format(self.avatar.name))
      self.avatar = None
      self.state = self.s_loggedin
      return Success()
    
    else:
      return self.avatar.act(action)
