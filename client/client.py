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
  
  def start(self, host, port, nport):
    self.control.connect(host, port)
    res = self.control.sendrecv(GetIdentity())
    if res.istype(Identity):
      self.identity = res.identity
      Thread(target=self.nstart, args=(host, nport)).start()
      print("Received client identity: {0}".format(self.identity))
    else:
      print("Failed to retrieve identity from server.")
  
  def nstart(self, host, port):
    self.notify.setmapping(send=ACTION_MAPPING, recv=RESPONSE_MAPPING)
    self.notify.connect(host, port)
    self.notify.send(Identify(self.identity))
    res = self.notify.recv()
    if res.istype(RemapNotify):
      print("Notify connection opened.")
      self.notify.setmapping(recv=NOTIFY_MAPPING, send={})
      
      while 1:
        res = self.notify.recv()
        if res:
          self.nhandle(res)
        else:
          break
    else:
      print("Failed to open notify connection.")
  
  def nhandle(self, n):
    ### todo
    print("Received notification: {0}".format(n.__class__))
  
  def login(self, user, password):
    if self.control.sendrecv(Login(user, password)).SUCCESS:
      print("Login success: {0}".format(user))
    else:
      print("Login failure: {0}".format(user))
  
  def charselect(self, char):
    if self.control.sendrecv(CharSelect(char)).SUCCESS:
      print("Character selected: {0}".format(char))
    else:
      print("Failed to select character: {0}.".format(char))
  
  def charquit(self):
    if self.control.sendrecv(CharQuit()).SUCCESS:
      print("Character quit success.")
    else:
      print("Character quit failure.")
  
  def logout(self):
    if self.control.sendrecv(Logout()).SUCCESS:
      print("Logout success.")
    else:
      print("Logout failure.")
    
  def quit(self):
    if self.control.sendrecv(Quit()).SUCCESS:
      self.control.close()
      self.notify.close()
      print("Quit success.")
    else:
      print("Quit failure.")
  

if __name__ == '__main__':
  c = CombatClient()
  c.start('127.0.0.1', 9994, 10004)
  c.login('Daniel', 'Test')
  c.charselect("Blastoise")
  c.charquit()
  c.logout()
  c.login('John', 'Hancock')
  c.quit()
  c.logout()
  c.quit()