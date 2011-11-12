#!/usr/bin/env python
#
# Client program to communicate with combat server

from threading import Thread
from wombat.stream import Stream
from wombat.control.mapping import ACTION_MAPPING, RESPONSE_MAPPING
from wombat.control.action import *
from wombat.control.response import *
from wombat.notify.mapping import NOTIFY_MAPPING

class CombatClient:
  def __init__(self):
    self.control = Stream(send=ACTION_MAPPING, recv=RESPONSE_MAPPING)
    self.notify = Stream()
    self.identity = None
    self.debug = []
  
  def start(self, host, port, nport):
    self.control.connect(host, port)
    res = self.control.sendrecv(GetIdentity())
    if res.istype(Identity):
      self.identity = res.identity
      Thread(target=self.nstart, args=(host, nport)).start()
      self.debug.append("Received client identity: {0}".format(self.identity))
    else:
      self.debug.append("Failed to retrieve identity from server.")
  
  def nstart(self, host, port):
    self.notify.setmapping(send=ACTION_MAPPING, recv=RESPONSE_MAPPING)
    self.notify.connect(host, port)
    self.notify.send(Identify(self.identity))
    res = self.notify.recv()
    if res.istype(RemapNotify):
      self.debug.append("Notify connection opened.")
      self.notify.setmapping(recv=NOTIFY_MAPPING, send={})
      
      while 1:
        res = self.notify.recv()
        if res:
          self.nhandle(res)
        else:
          break
    else:
      self.debug.append("Failed to open notify connection.")
  
  def nhandle(self, n):
    ### todo
    self.debug.append("Received notification: {0}".format(n.__class__))
  
  def login(self, user, password):
    if self.control.sendrecv(Login(user, password)).SUCCESS:
      self.debug.append("Login success: {0}".format(user))
    else:
      self.debug.append("Login failure: {0}".format(user))
  
  def charselect(self, char):
    if self.control.sendrecv(CharSelect(char)).SUCCESS:
      self.debug.append("Character selected: {0}".format(char))
    else:
      self.debug.append("Failed to select character: {0}.".format(char))
  
  def charquit(self):
    if self.control.sendrecv(CharQuit()).SUCCESS:
      self.debug.append("Character quit success.")
    else:
      self.debug.append("Character quit failure.")
  
  def logout(self):
    if self.control.sendrecv(Logout()).SUCCESS:
      self.debug.append("Logout success.")
    else:
      self.debug.append("Logout failure.")
    
  def quit(self):
    if self.control.sendrecv(Quit()).SUCCESS:
      self.control.close()
      self.notify.close()
      self.debug.append("Quit success.")
    else:
      self.debug.append("Quit failure.")
  

if __name__ == '__main__':
  from cli import ClientShell
  ClientShell().cmdloop()