#!/usr/bin/env python
#
# Runs a combat server

from random import randrange
from wombat.stream import Stream
from wombat.notify.mapping import NOTIFY_MAPPING
from wombat.notify.notification import NotifyKey
from wombat.control.mapping import ACTION_MAPPING, RESPONSE_MAPPING
from client import Client
from threading import Thread
from select import select
from socket import socket, AF_INET, SOCK_STREAM

class CombatServer:
  LISTEN_BACKLOG = 5
  
  def __init__(self):
    # map of clients by their control sockets
    self.clients = {}
    
    # map of anonymous notify streams by their claim key
    self._anstreams = {}
    
    # listener sockets for incoming control and notify connections
    self._clistens = socket(AF_INET, SOCK_STREAM)
    self._nlistens = socket(AF_INET, SOCK_STREAM)
  
  def debug(self, message):
    print(message)
  
  def start(self, host, cport, nport):
    Thread(target=self._clisten, args=(host, cport)).start()
    Thread(target=self._nlisten, args=(host, nport)).start()
    
    # process client actions
    while 1:
      if len(self.clients):
        # must pass 0 as timeout so new clients will always be checked
        for sock in select(self.clients.keys(), [], [], 0)[0]:
          Thread(target=self.clients[sock].act).start()
  
  def claimnotify(self, key):
    """ Claims an anonymous notify socket, returning and dereferencing it. """
    notify = self._anstreams.get(key, None)
    if notify:
      del self._anstreams[key]
      return notify
    else:
      return None
  
  def _clisten(self, host, port):
    """ Listens for incoming control connections. """
    self._clistens.bind((host, port))
    self._clistens.listen(self.LISTEN_BACKLOG)
    while 1:
      sock, addr = self._clistens.accept()
      self.connect(sock, addr)
  
  def _nlisten(self, host, port):
    """
    Listens for incoming notify connections and adds them to the list of 
    anonymous notify streams, to later be claimed by a client. Sends the claim
    key to the client for this purpose.
    """
    self._nlistens.bind((host, port))
    self._nlistens.listen(self.LISTEN_BACKLOG)
    while 1:
      sock, addr = self._nlistens.accept()
      key = randrange(65535) # this will need to be more secure in the future
      self._anstreams[key] = Stream(sock, send=NOTIFY_MAPPING)
      self._anstreams[key].send(NotifyKey(key))
  
  def connect(self, control, addr):
    """ Connects a client, given its control socket and address. """
    self.clients[control] = Client(self, Stream(control, recv=ACTION_MAPPING, 
                                                send=RESPONSE_MAPPING), addr)
    self.clients[control].debug("Connected")
  
  def disconnect(self, control):
    """
    Disconnects a client, given its control socket.
    TODO: Make this actually close the control and notify connections... be
          careful with locking.
    """
    client = self.clients.get(control, None)
    if client:
      del self.clients[control] # delete first so no more actions
      client.debug("Disconnected")
  
  def clientbychar(self, char):
    """
    Returns a client, given their character name. When we want to get serious 
    about this, we should map them. For now, this O(n) algo is cleaner.
    """
    for c in self.clients.values():
      if c.char == char:
        return c
    return None

if __name__ == "__main__":
  CombatServer().start("127.0.0.1", 10000, 10001)
