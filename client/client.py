#!/usr/bin/env python
#
# Client program to communicate with combat server

from threading import Thread
from socket import socket, AF_INET, SOCK_STREAM
from wombat.stream import Stream
from wombat.control.mapping import ACTION_MAPPING, RESPONSE_MAPPING
from wombat.control.action import *
from wombat.control.response import *
from wombat.notify.mapping import NOTIFY_MAPPING
from wombat.notify.notification import *

class CombatClient:
  def __init__(self):
    self.scontrol = socket(AF_INET, SOCK_STREAM)
    self.snotify = socket(AF_INET, SOCK_STREAM)
    self.control = Stream(self.scontrol, send=ACTION_MAPPING,
                          recv=RESPONSE_MAPPING)
    self.notify = Stream(self.snotify, recv=NOTIFY_MAPPING)
    self.debugs = []
  
  def debug(self, msg):
    self.debugs.append(msg)
  
  def start(self, host, cport, nport):
    self.scontrol.connect((host, cport))
    nt = Thread(target=self.nstart, args=(host, nport))
    nt.daemon = True
    nt.start()
  
  def nstart(self, host, port):
    self.snotify.connect((host, port))
    key = self.notify.recv()
    if isinstance(key, NotifyKey):
      res = self.control.sendrecv(ClaimNotify(key.key))
      if res.SUCCESS:
        while 1:
          res = self.notify.recv()
          if res:
            self.nhandle(res)
          else:
            break
      else:
        self.debug("Failed to claim notify connection.")
    else:
      self.debug("Failed to receive ClaimKey on notify connection.")
  
  def nhandle(self, n):
    if isinstance(n, RecvMessage):
      self.debug("[{0}]: {1}".format(n.char, n.message))
    else:
      self.debug("Received notification: {0}".format(n.__class__))
  
  def login(self, user, password):
    if self.control.sendrecv(Login(user, password)).SUCCESS:
      self.debug("Login success: {0}".format(user))
    else:
      self.debug("Login failure: {0}".format(user))
  
  def charselect(self, char):
    if self.control.sendrecv(CharSelect(char)).SUCCESS:
      self.debug("Character selected: {0}".format(char))
    else:
      self.debug("Failed to select character: {0}.".format(char))
  
  def charquit(self):
    if self.control.sendrecv(CharQuit()).SUCCESS:
      self.debug("Character quit success.")
    else:
      self.debug("Character quit failure.")
  
  def logout(self):
    if self.control.sendrecv(Logout()).SUCCESS:
      self.debug("Logout success.")
    else:
      self.debug("Logout failure.")
    
  def quit(self):
    if self.control.sendrecv(Quit()).SUCCESS:
      self.control.socket.close()
      self.notify.socket.close()
      self.debug("Quit success.")
      return True
    else:
      self.debug("Quit failure.")
      return False
  
  def sendmessage(self, char, message):
    res = self.control.sendrecv(SendMessage(char, message))
    if res.SUCCESS:
      self.debug("Message sent.")
    elif isinstance(res, CharNoExists):
      self.debug("Character does not exist: {0}".format(res.char))
    else:
      self.debug("Failed to send message.")

if __name__ == '__main__':
  from argparse import ArgumentParser
  parser = ArgumentParser(description="Interactive combat client shell.")
  parser.add_argument('-r', default='127.0.0.1')
  parser.add_argument('-c', type=int, default=10000)
  parser.add_argument('-n', type=int, default=10001)
  args = parser.parse_args()
  client = CombatClient()
  client.start(args.r, args.c, args.n)
  
  from cli import ClientShell
  ClientShell(client).cmdloop()