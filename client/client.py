#!/usr/bin/env python

from threading import Thread, Lock
from socket import socket, AF_INET, SOCK_STREAM

from wombat.stream import Stream
from wombat.control.mapping import ACTION_MAPPING, RESPONSE_MAPPING
from wombat.control.action import *
from wombat.control.response import *
from wombat.notify.mapping import NOTIFY_MAPPING
from wombat.notify.notification import *

class CombatClient:
  def __init__(self):
    self.control = socket(AF_INET, SOCK_STREAM)
    self.lcontrol = Lock()
    self.notify = socket(AF_INET, SOCK_STREAM)
    self.wcontrol = Stream(send=ACTION_MAPPING, recv=RESPONSE_MAPPING)
    self.wnotify = Stream(recv=NOTIFY_MAPPING)
    self.debugs = []
    self.nhook = self.ndebug
    
    self.user = None
    self.avatar = None
  
  def debug(self, msg):
    self.debugs.append(msg)
  
  def start(self, host, cport, nport):
    self.control.connect((host, cport))
    nt = Thread(target=self.nstart, args=(host, nport))
    nt.daemon = True
    nt.start()
  
  def nstart(self, host, port):
    self.notify.connect((host, port))
    key = self.wnotify.recv(self.notify)
    if isinstance(key, NotifyKey):
      with self.lcontrol:
        res = self.wcontrol.sendrecv(self.control, ClaimNotify(key.key))
      if res.SUCCESS:
        while 1:
          self.nhook(self.wnotify.recv(self.notify))
      else:
        self.debug("Failed to claim notify connection.")
    else:
      self.debug("Failed to receive ClaimKey on notify connection.")
  
  def ndebug(self, n):
    if isinstance(n, RecvMessage):
      self.debug("[{0}]: {1}".format(n.avatar, n.message))
    else:
      self.debug("Received notification: {0}".format(n.__class__))
  
  def login(self, user, password):
    with self.lcontrol:
      res = self.wcontrol.sendrecv(self.control, Login(user, password))
      if res.SUCCESS:
        self.user = user
        self.debug("Login success: {0}".format(user))
      else:
        self.debug("Login failure: {0}".format(user))
      return res
  
  def avatarselect(self, avatar):
    with self.lcontrol:
      res = self.wcontrol.sendrecv(self.control, AvatarSelect(avatar))
      if res.SUCCESS:
        self.avatar = avatar
        self.debug("Avatar selected: {0}".format(avatar))
      else:
        self.debug("Failed to select character: {0}.".format(avatar))
      return res
  
  def avatarquit(self):
    with self.lcontrol:
      res = self.wcontrol.sendrecv(self.control, AvatarQuit())
      if res.SUCCESS:
        self.avatar = None
        self.debug("Avatar quit success.")
      else:
        self.debug("Avatar quit failure.")
      return res
  
  def logout(self):
    with self.lcontrol:
      res = self.wcontrol.sendrecv(self.control, Logout())
      if res.SUCCESS:
        self.user = None
        self.debug("Logout success.")
      else:
        self.debug("Logout failure.")
      return res
    
  def quit(self):
    with self.lcontrol:
      res = self.wcontrol.sendrecv(self.control, Quit())
      if res.SUCCESS:
        self.debug("Quit success.")
      else:
        self.debug("Quit failure.")
      return res
  
  def sendmessage(self, avatar, message):
    with self.lcontrol:
      res = self.wcontrol.sendrecv(self.control, SendMessage(avatar, message))
      if res.SUCCESS:
        self.debug("Message sent.")
      elif isinstance(res, AvatarNoExists):
        self.debug("Avatar does not exist: {0}".format(res.avatar))
      else:
        self.debug("Failed to send message.")
      return res

if __name__ == '__main__':
  from argparse import ArgumentParser
  parser = ArgumentParser(description="Combat client application.")
  parser.add_argument('-g', action='store_true')
  parser.add_argument('-r', default='127.0.0.1')
  parser.add_argument('-c', type=int, default=10000)
  parser.add_argument('-n', type=int, default=10001)
  args = parser.parse_args()
  client = CombatClient()
  client.start(args.r, args.c, args.n)
  
  if args.g:
    from gui import ClientUI
    ClientUI(client).start()
  else:
    from cli import ClientShell
    ClientShell(client).cmdloop()