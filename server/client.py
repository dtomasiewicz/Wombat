from wombat.control.action import *
from wombat.control.response import *

from combatserver.threads import Lockable

class Client(Lockable):
  """
  Handles all actions that a client machine can perform.
  
  Public threading:
    must be acquired before mutation, invocation, and dependent accesses
  """
  
  def __init__(self, server, control):
    super().__init__()
    self.server = server
    self.control = control
    self.notify = None
    self.user = None
    self.avatar = None
    self.state = self.s_start
  
  def fileno(self):
    return self.control.fileno()
  
  def identity(self):
    """ Unique string identifying the client, composed of socket id and IP. """
    return "{0}".format(id(self))
  
  def debug(self, msg):
    """ Sends client-relevant debugging info to the server. """
    self.server.debug("{0}: {1}".format(self.identity(), msg))
  
  def s_start(self, action):
    """
    Client state after opening the client application or after logging out.
    Valid actions: ClaimNotify, Login, Quit
    """
    if isinstance(action, Login):
      self.user = action.user
      self.state = self.s_loggedin
      return Success()
      
    elif isinstance(action, Quit):
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
      self.user = None
      self.state = self.s_start
      return Success()
        
    elif isinstance(action, AvatarSelect):
      self.avatar = self.server.avatar(action.avatar)
      if self.avatar:
        with self.avatar:
          self.avatar.client = self
        self.state = self.s_avatarselected
        return Success()
      else:
        return AvatarNoExists(action.avatar)
      
    else:
      return InvalidAction()
  
  def s_avatarselected(self, action):
    """
    Client state after selecting an avatar.
    """
    with self.avatar:
      if isinstance(action, AvatarQuit):
        self.avatar.client = None
        self.avatar = None
        self.state = self.s_loggedin
        return Success()
      
      else:
        return self.avatar.act(action)
