from threading import Thread
from wombat.control.action import GetIdentity, Login, Logout, Quit, CharSelect, CharQuit
from wombat.control.response import Identity, Success, InvalidAction
from wombat.control.mapping import ACTION_MAPPING, RESPONSE_MAPPING
from wombat.notify.notification import Test

class Client:
  # control stream should have control mappings
  def __init__(self, server, identity, control):
    self.server = server
    self.control = control
    self.identity = identity
    self.notify = None
    self.user = None
    self.char = None
  
  def sendnotify(self, msg):
    if self.notify:
      self.notify.send(msg)
    else:
      print("Warning: failed to notify client({0}) of {1}".format(self.identity, msg.__class__))
  
  # initial client state
  def start(self):
    print("Client connected: {0}".format(self.identity))
    
    while 1:
      action = self.control.recv()
      
      if not action:
        break
        
      elif action.istype(GetIdentity):
        print("Client requested identity: {0}".format(self.identity))
        self.control.send(Identity(self.identity))
      
      elif action.istype(Login):
        self.user = action.user
        print("{0} logged in to client: {1}".format(self.user, self.identity))
        self.control.send(Success())
        self.sendnotify(Test())
        self.sloggedin()
        
      elif action.istype(Quit):
        self.control.send(Success())
        print("Client quit: {0}".format(self.identity))
        break
        
      else:
        self.control.send(InvalidAction())
  
  # client logged in
  # accepts CharSelect, Logout
  def sloggedin(self):
    while self.user:
      action = self.control.recv()
      
      if not action:
        self.user = None
      
      elif action.istype(Logout):
        print("{0} logged out.".format(self.user))
        self.user = None
        self.control.send(Success())
        
      elif action.istype(CharSelect):
        self.char = action.char
        print("{0} selected {1}.".format(self.user, self.char))
        self.control.send(Success())
        self.scharselected()
        
      else:
        self.control.send(InvalidAction())
  
  # once a client selects a character, they are responsible for establishing
  # a notification connection
  def scharselected(self):
    while self.char:
      action = self.control.recv()
      
      if not action:
        self.char = None
      
      elif action.istype(CharQuit):
        print("{0} deselected {1}.".format(self.user, self.char))
        self.char = None
        self.control.send(Success())
        
      else:
        self.control.send(InvalidAction())
