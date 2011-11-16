#!/usr/bin/env python

from threading import Thread
from select import select
from socket import socket, AF_INET, SOCK_STREAM
from random import randrange
from time import time, sleep

from wombat.stream import Stream
from wombat.notify.mapping import NOTIFY_MAPPING
from wombat.notify.notification import NotifyKey
from wombat.control.mapping import ACTION_MAPPING, RESPONSE_MAPPING

from combatserver.client import Client

class CombatServer:
  LISTEN_BACKLOG = 5
  SELECT_TIMEOUT = .001
  
  def __init__(self):
    # listener sockets for incoming control and notify connections
    self._clisten = socket(AF_INET, SOCK_STREAM)
    self._nlisten = socket(AF_INET, SOCK_STREAM)
  
  def debug(self, message):
    print(message)
    #pass
  
  def start(self, host, cport, nport):
    # map of clients by their control sockets
    self.clients = {}
    
    # map of anonymous notify streams by their claim key
    self._anstreams = {}
    
    # listens for incoming control connections
    self._clisten.bind((host, cport))
    self._clisten.setblocking(0)
    self._clisten.listen(self.LISTEN_BACKLOG)
    
    # listens for incoming notify connections
    self._nlisten.bind((host, nport))
    self._nlisten.setblocking(0)
    self._nlisten.listen(self.LISTEN_BACKLOG)
    
    # set of idle connections to be select()ed from
    self.idle = set((self._clisten, self._nlisten))
    
    # cleanup daemon for unclaimed notify threads
    cleanup = Thread(target=self.cleanup)
    cleanup.daemon = True
    cleanup.start()
    
    while 1:
      if len(self.idle):
        for sock in select(self.idle, [], [], self.SELECT_TIMEOUT)[0]:
          self.idle.remove(sock)
          if sock == self._clisten:
            Thread(target=self._caccept).start()
          elif sock == self._nlisten:
            Thread(target=self._naccept).start()
          else:
            Thread(target=self.clients[sock].act).start()
      elif self.SELECT_TIMEOUT > 0:
        sleep(self.SELECT_TIMEOUT)
  
  def cleanup(self):
    while 1:
      for key, notify in tuple(self._anstreams.items()):
        with notify.lock:
          if self._anstreams.get(key, None) and time() > notify.created + 5:
            notify.socket.close()
            del self._anstreams[key]
      sleep(5)
  
  def claimnotify(self, key):
    """
    Claims an anonymous notify socket, returning and dereferencing it.
    Since notify sockets become a shared resource once they are placed in 
    _anstreams, we must ensure we have the stream's lock AND it is still in
    _anstreams before handing it to the client.
    """
    notify = self._anstreams.get(key, None)
    if notify:
      with notify.lock:
        # must get it again, in case it was claimed before we acquired the lock
        notify = self._anstreams.get(key, None)
        if notify:
          del self._anstreams[key]
        return notify
    else:
      return None
  
  def _caccept(self):
    """ Connects a new client. """
    sock, addr = self._clisten.accept()
    self.idle.add(self._clisten)
    
    sock.setblocking(0)
    self.clients[sock] = Client(self, Stream(sock, recv=ACTION_MAPPING, 
                                             send=RESPONSE_MAPPING), addr)
    self.clients[sock].debug("Connected")
    self.idle.add(sock)
  
  def _naccept(self):
    """
    Accepts an incoming notify connection and adds it to the list of anonymous 
    notify streams, to later be claimed by a client. Sends the claim key to the
    client for this purpose.
    """
    sock, addr = self._nlisten.accept()
    self.idle.add(self._nlisten)
    
    sock.setblocking(0)
    key = randrange(65535) # this will need to be more secure in the future
    self._anstreams[key] = Stream(sock, send=NOTIFY_MAPPING)
    self._anstreams[key].send(NotifyKey(key))
  
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
  server = CombatServer()
  try:
    server.start("127.0.0.1", 10000, 10001)
  except KeyboardInterrupt:
    pass
