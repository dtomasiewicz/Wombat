#!/usr/bin/env python
#
# Runs a combat server

from random import randrange
from wombat.stream import Stream
from wombat.notify.mapping import NOTIFY_MAPPING
from wombat.notify.notification import NotifyKey
from client import Client
from threading import Thread
from select import select
from socket import socket, AF_INET, SOCK_STREAM

class CombatServer:
  LISTEN_BACKLOG = 5
  
  def __init__(self):
    # map of clients by their control sockets
    self.clients = {}
    # list of anonymous notify sockets (not yet associated with a client)
    self.anstreams = {}
    
    # listener sockets for control and notify sockets
    self.clistens = socket(AF_INET, SOCK_STREAM)
    self.nlistens = socket(AF_INET, SOCK_STREAM)
  
  def start(self, host, cport, nport):
    # listen for incoming control connections
    Thread(target=self.clisten, args=(host, cport)).start()
    
    # listen for incoming notify connections
    Thread(target=self.nlisten, args=(host, nport)).start()
    
    # handle sockets that are ready for reading
    while 1:
      if len(self.clients):
        for sock in select(self.clients.keys(),[],[])[0]:
          Thread(self.clients[sock].act())
  
  def claimnotify(self, key):
    print("in claimnotify")
    notify = self.anstreams.get(key, None)
    if notify:
      del self.anstreams[key]
      return notify
    else:
      return None
  
  # listens for incoming control connections
  def clisten(self, host, port):
    self.clistens.bind((host, port))
    self.clistens.listen(self.LISTEN_BACKLOG)
    while 1:
      sock, addr = self.clistens.accept()
      self.connect(sock)
  
  # listens for incoming notify connections and appends them to the list of
  # anonymous notify streams, later to be claimed by a client
  def nlisten(self, host, port):
    self.nlistens.bind((host, port))
    self.nlistens.listen(self.LISTEN_BACKLOG)
    while 1:
      sock, addr = self.nlistens.accept()
      key = randrange(65535)
      self.anstreams[key] = Stream(sock, send=NOTIFY_MAPPING)
      self.anstreams[key].send(NotifyKey(key))
  
  # connects a client, given its control socket, returning the client identity
  def connect(self, control):
    self.clients[control] = Client(self, control)
    print("Client {0} connected".format(id(control)))
  
  # disconnects a client, given its control socket
  def disconnect(self, control):
    client = self.clients.get(control, None)
    if client:
      del self.clients[control] # delete first so no more actions
      control.close()
      if client.notify:
        client.notify.socket.close()
      print("Client {0} disconnected".format(id(control)))

if __name__ == "__main__":
  CombatServer().start("127.0.0.1", 10000, 10001)