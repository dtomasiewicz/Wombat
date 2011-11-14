from wombat.control.action import *
from wombat.control.response import *
from wombat.notify.notification import *

class Client:
  """ Handles all actions that a client machine can perform. """
  
  def __init__(self, server, control, address):
    self.server = server
    self.control = control
    self.address = address
    self.notify = None
    self.user = None
    self.char = None
    self.state = self.sinitial
  
  def sendnotify(self, msg):
    with self.notify.lock:
      """ Sends the the given Notification message to the client. """
      if self.notify:
        self.notify.send(msg)
      else:
        self.debug("Failed to be notified of {0}".format(msg.__class__))
  
  def identity(self):
    """ Unique string identifying the client, composed of socket id and IP. """
    return "{0}@{1}".format(id(self.control.socket), self.address[0])
  
  def debug(self, msg):
    """ Sends client-relevant debugging info to the server. """
    self.server.debug("{0}: {1}".format(self.identity(), msg))
  
  def act(self):
    """ Handles an Action message received from the client. """
    with self.control.lock:
      action = self.control.recv()
      if action and isinstance(action, ClaimNotify):
        self.notify = self.server.claimnotify(action.key)
        if self.notify:
          self.control.send(Success())
        else:
          self.control.send(InvalidNotifyKey())
      elif not action or self.state(action) == True:
        self.server.disconnect(self.control.socket)
  
  def sinitial(self, action):
    """
    Client state after opening the client application.
    Valid actions: Login, Quit
    """
    if isinstance(action, Login):
      self.user = action.user
      self.debug("Logged in as {0}".format(self.user))
      self.state = self.sloggedin
      self.control.send(Success())
      
    elif isinstance(action, Quit):
      self.debug("Quit")
      self.control.send(Success())
      return True
      
    else:
      self.control.send(InvalidAction())
  
  def sloggedin(self, action):
    """
    Client state after logging in.
    Valid actions: Logout, CharSelect
    """
    if isinstance(action, Logout):
      self.debug("Logged out")
      self.user = None
      self.state = self.sinitial
      self.control.send(Success())
        
    elif isinstance(action, CharSelect):
      self.char = action.char
      self.debug("Selected {0}".format(self.char))
      self.state = self.scharselected
      self.control.send(Success())
      
    else:
      self.control.send(InvalidAction())
  
  def scharselected(self, action):
    """
    Client state after selecting a character.
    Valid actions: CharQuit, SendMessage
    """
    if isinstance(action, CharQuit):
      self.debug("Deselected {0}".format(self.char))
      self.char = None
      self.state = self.sloggedin
      self.control.send(Success())
      
    elif isinstance(action, SendMessage):
      char = self.server.clientbychar(action.char)
      if char:
        self.debug("Messaged {0}".format(action.char))
        char.sendnotify(RecvMessage(self.char, action.message))
        self.control.send(Success())
      else:
        self.control.send(CharNoExists(action.char))
    
    else:
      self.control.send(InvalidAction())
