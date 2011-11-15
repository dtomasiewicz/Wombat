from socket import error as socketerror
from struct import error as structerror
from select import select
from errno import errorcode

from wombat.message import CodeError
from wombat.control.action import *
from wombat.control.response import *
from wombat.notify.notification import *

class Client:
  """
  Handles all actions that a client machine can perform. For thread safety,
  should never be mutated except through the act() method and methods that are
  called by act().
  """
  
  def __init__(self, server, control, address):
    self.server = server
    self._control = control
    self.address = address
    self._notify = None
    self.user = None
    self.char = None
    self._state = self._sinitial
  
  def sendnotify(self, msg):
    """ Sends the the given Notification message to this client. """
    if self._notify:
      with self._notify.lock:
        self._notify.send(msg)
    else:
      self.debug("Failed to be notified of {0}".format(msg.__class__))
  
  def identity(self):
    """ Unique string identifying the client, composed of socket id and IP. """
    return "{0}@{1}".format(id(self._control.socket), self.address[0])
  
  def debug(self, msg):
    """ Sends client-relevant debugging info to the server. """
    self.server.debug("{0}: {1}".format(self.identity(), msg))
    
  def act(self):
    """
    Handles an Action message received from the client. If the socket has more
    data after the first message is read, it will immediately read the next,
    continuing until there are no more.
    """
    dc = False
    while not dc:
      try:
        action = self._control.recv()
      except CodeError as e:
        self.debug("Received invalid message code: {0}".format(e.code))
        dc = True
      except socketerror as e:
        self.debug("{0} occurred during message reception", errorcode[e.errno])
        dc = True
      except structerror as e:
        self.debug("Failed to unpack message data")
        dc = True
      
      if isinstance(action, ClaimNotify):
        self._notify = self.server.claimnotify(action.key)
        if self._notify:
          self._control.send(Success())
        else:
          self._control.send(InvalidNotifyKey())
      else:
        dc = self._state(action)
        
      # only continue processing if more data on socket
      if len(select([self._control.socket], [], [])[0]) == 0:
        break
    
    if dc:
      self.server.disconnect(self._control.socket)
    else:
      self.server.idle.add(self._control.socket)
  
  def _sinitial(self, action):
    """
    Client state after opening the client application or after logging out.
    Valid actions: Login, Quit
    """
    
    if isinstance(action, Login):
      self.user = action.user
      self.debug("Logged in as {0}".format(self.user))
      self._state = self._sloggedin
      self._control.send(Success())
      
    elif isinstance(action, Quit):
      self.debug("Quit")
      self._control.send(Success())
      return True
      
    else:
      self._control.send(InvalidAction())
  
  def _sloggedin(self, action):
    """
    Client state after logging in or deselecting a character.
    Valid actions: Logout, CharSelect
    """
    
    if isinstance(action, Logout):
      self.debug("Logged out")
      self.user = None
      self._state = self._sinitial
      self._control.send(Success())
        
    elif isinstance(action, CharSelect):
      self.char = action.char
      self.debug("Selected {0}".format(self.char))
      self._state = self._scharselected
      self._control.send(Success())
      
    else:
      self._control.send(InvalidAction())
  
  def _scharselected(self, action):
    """
    Client state after selecting a character.
    Valid actions: CharQuit, SendMessage
    """
    
    if isinstance(action, CharQuit):
      self.debug("Deselected {0}".format(self.char))
      self.char = None
      self._state = self._sloggedin
      self._control.send(Success())
      
    elif isinstance(action, SendMessage):
      char = self.server.clientbychar(action.char)
      if char:
        self.debug("Messaged {0}".format(action.char))
        char.sendnotify(RecvMessage(self.char, action.message))
        self._control.send(Success())
      else:
        self._control.send(CharNoExists(action.char))
    
    else:
      self._control.send(InvalidAction())
