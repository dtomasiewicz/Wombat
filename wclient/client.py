#!/usr/bin/env python

from threading import Thread, Lock
from socket import socket, AF_INET, SOCK_STREAM

from wproto.stream import Stream

from wshared.control.game import *
from wshared.control.realm import *
from wshared.notify.game import *
from wshared.notify.realm import *

def extend_map(m1, m2):
  new = m1.copy()
  new.update(m2)
  return new

class CombatClient:
  def __init__(self):
    self.control = Stream(send=extend_map(GAME_ACTION, REALM_ACTION),
                          recv=extend_map(GAME_RESPONSE, REALM_RESPONSE))
    self.notify = Stream(recv=extend_map(GAME_NOTIFY, REALM_NOTIFY))
    self.lcontrol = Lock()
    self.debugs = []
    self.nhook = self.ndebug
    self.avatar = None
  
  def debug(self, msg):
    self.debugs.append(msg)
  
  def start(self, host, cport, nport):
    self.control.connect(host, cport)
    nt = Thread(target=self.nstart, args=(host, nport))
    nt.daemon = True
    nt.start()
  
  def nstart(self, host, port):
    self.notify.connect(host, port)
    key = self.notify.recv()
    if isinstance(key, NotifyKey):
      with self.lcontrol:
        res = self.control.sendrecv(ClaimNotify(key.key))
      if res.SUCCESS:
        while 1:
          self.nhook(self.notify.recv())
      else:
        self.debug("Failed to claim notify connection.")
    else:
      self.debug("Failed to receive ClaimKey on notify connection.")
  
  def ndebug(self, n):
    if isinstance(n, RecvMessage):
      self.debug("[{0}]: {1}".format(n.avatar, n.message))
    else:
      self.debug("Received notification: {0}".format(n.__class__))
  
  def avatarselect(self, avatar):
    with self.lcontrol:
      res = self.control.sendrecv(SelectAvatar(avatar))
      if res.SUCCESS:
        self.avatar = avatar
        self.debug("Avatar selected: {0}".format(avatar))
      elif isinstance(res, AvatarInUse):
        self.debug("Avatar in use: {0}.".format(avatar))
      else:
        self.debug("Failed to select avatar: {0}".format(avatar))
      return res
  
  def avatarquit(self):
    with self.lcontrol:
      res = self.control.sendrecv(QuitAvatar())
      if res.SUCCESS:
        self.avatar = None
        self.debug("Avatar quit success.")
      else:
        self.debug("Avatar quit failure.")
      return res
    
  def quit(self):
    with self.lcontrol:
      res = self.control.sendrecv(Quit())
      if res.SUCCESS:
        self.debug("Quit success.")
      else:
        self.debug("Quit failure.")
      return res
  
  def sendmessage(self, avatar, message):
    with self.lcontrol:
      res = self.control.sendrecv(SendMessage(avatar, message))
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
