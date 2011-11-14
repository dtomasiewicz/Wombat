from threading import Thread
from wombat.stream import Stream
from wombat.control.action import ClaimNotify, Login, Logout, Quit, CharSelect, CharQuit
from wombat.control.response import Success, InvalidAction
from wombat.control.mapping import ACTION_MAPPING, RESPONSE_MAPPING
from wombat.notify.notification import Test

class Client:
  # control stream should have control mappings
  def __init__(self, server, control):
    self.server = server
    self.control = Stream(control, recv=ACTION_MAPPING, send=RESPONSE_MAPPING)
    self.notify = None
    self.user = None
    self.char = None
    self.state = self.sinitial
  
  def sendnotify(self, msg):
    if self.notify:
      self.notify.send(msg)
    else:
      print("Warning: failed to notify client {0} of {1}".format(id(self.control.socket), msg.__class__))
  
  # return True if client should disconnect
  def act(self):
    action = self.control.recv()
    if action and action.istype(ClaimNotify):
      self.notify = self.server.claimnotify(action.key)
      if self.notify:
        self.control.send(Success())
      else:
        self.control.send(InvalidNotifyKey())
    elif not action or self.state(action) == True:
      self.server.disconnect(self.control.socket)
  
  # initial client state
  def sinitial(self, action):
    if action.istype(Login):
      self.user = action.user
      print("{0} logged in to client: {1}".format(self.user, id(self.control.socket)))
      self.state = self.sloggedin
      self.control.send(Success())
      self.sendnotify(Test())
      
    elif action.istype(Quit):
      print("Client quit: {0}".format(id(self.control.socket)))
      self.control.send(Success())
      return True
      
    else:
      self.control.send(InvalidAction())
  
  # client logged in
  # accepts CharSelect, Logout
  def sloggedin(self, action):
    if action.istype(Logout):
      print("{0} logged out.".format(self.user))
      self.user = None
      self.state = self.sinitial
      self.control.send(Success())
        
    elif action.istype(CharSelect):
      self.char = action.char
      print("{0} selected {1}.".format(self.user, self.char))
      self.state = self.scharselected
      self.control.send(Success())
      
    else:
      self.control.send(InvalidAction())
  
  def scharselected(self, action):
    if action.istype(CharQuit):
      print("{0} deselected {1}.".format(self.user, self.char))
      self.char = None
      self.state = self.sloggedin
      self.control.send(Success())
      
    else:
      self.control.send(InvalidAction())
