#!/usr/bin/env python

from threading import Thread
from select import select
from socket import socket, AF_INET, SOCK_STREAM
from random import randrange
from time import time, sleep

from wombat.stream import Stream
from wombat.notify.mapping import NOTIFY_MAPPING
from wombat.notify.notification import *
from wombat.control.mapping import ACTION_MAPPING, RESPONSE_MAPPING

from combatserver.client import Client
from combatserver.avatar import Avatar

class CombatServer:
  LISTEN_BACKLOG = 5
  SELECT_TIMEOUT = .001
  
  def __init__(self):
    # listener sockets for incoming control and notify connections
    self._clisten = socket(AF_INET, SOCK_STREAM)
    self._nlisten = socket(AF_INET, SOCK_STREAM)
    
    # stream wrappers for control and notify connections
    self._controlw = Stream(recv=ACTION_MAPPING, send=RESPONSE_MAPPING)
    self._notifyw = Stream(send=NOTIFY_MAPPING)
  
  def debug(self, message):
    print(message)
  
  def start(self, host, cport, nport):
    # map of clientinfo tuples by their control sockets
    self._clients = {}
    
    # map of anonymous notify streams by their claim key
    self._anotifys = {}
    
    # listens for incoming control connections
    self._clisten.bind((host, cport))
    self._clisten.setblocking(0)
    self._clisten.listen(self.LISTEN_BACKLOG)
    
    # listens for incoming notify connections
    self._nlisten.bind((host, nport))
    self._nlisten.setblocking(0)
    self._nlisten.listen(self.LISTEN_BACKLOG)
    
    # set of idle connections to be select()ed from
    self._idle = set((self._clisten, self._nlisten))
    
    # cleanup daemon for unclaimed notify threads
    #cleanup = Thread(target=self.cleanup)
    #cleanup.daemon = True
    #cleanup.start()
    
    while 1:
      if len(self._idle):
        for sock in select(self._idle, [], [], self.SELECT_TIMEOUT)[0]:
          self._idle.remove(sock)
          if sock == self._clisten:
            Thread(target=self._caccept).start()
          elif sock == self._nlisten:
            Thread(target=self._naccept).start()
          else:
            Thread(target=self._clientdata, args=(self._clients[sock],)).start()
      elif self.SELECT_TIMEOUT > 0:
        sleep(self.SELECT_TIMEOUT)
  
  def _clientdata(self, client):
    while client.state:
      try:
        action = self._controlw.recv(client.control)
      except:
        """
        if isinstance(e, CodeError):
          self.debug("Received invalid message code: {0}".format(e.code))
        elif isinstance(e, socketerror):
          self.debug("{0} occurred during message reception".format(errorcode[e.errno]))
        elif isinstance(e, structerror):
          self.debug("Failed to unpack message data")
        """
        client.state = None
      else:
        with client:
          res = client.state(action)
        self._controlw.send(client.control, res)
        
        # only continue processing if more data on socket
        if len(select([client.control], [], [], 0)[0]) == 0:
          break
    
    if not client.state:
      self._disconnect(client)
    else:
      self._idle.add(client.control)
  
  """
  def cleanup(self):
    while 1:
      for key, notify in tuple(self._anstreams.items()):
        with notify.lock:
          # make sure the stream wasn't claimed while waiting for lock
          if self._anstreams.get(key, None) and time() > notify.created + 5:
            notify.socket.close()
            del self._anstreams[key]
      sleep(5)
  """
  
  def claimnotify(self, key):
    """
    Claims an anonymous notify socket, returning and dereferencing it.
    """
    notify = self._anotifys.get(key, None)
    if notify:
      del self._anotifys[key]
      return notify
    else:
      return None
  
  def _caccept(self):
    """ Connects a new client. """
    sock, addr = self._clisten.accept()
    self._idle.add(self._clisten)
    
    sock.setblocking(0)
    self._clients[sock] = Client(self, sock, addr)
    self._clients[sock].debug("Connected")
    self._idle.add(sock)
  
  def _naccept(self):
    """
    Accepts an incoming notify connection and adds it to the list of anonymous 
    notify streams, to later be claimed by a client. Sends the claim key to the
    client for this purpose.
    """
    sock, addr = self._nlisten.accept()
    self._idle.add(self._nlisten)
    
    sock.setblocking(0)
    key = randrange(65535) # this will need to be more secure in the future
    self._anotifys[key] = sock
    self._notifyw.send(sock, NotifyKey(key))
  
  def _disconnect(self, client):
    """ Disconnects a client. """
    del self._clients[client.control]
    with client:
      client.control.close()
      if client.notify:
        client.notify.close()
      if client.avatar:
        with client.avatar:
          client.avatar.setclient(None)
  
  def message(self, to, from_, message):
    """
    Sends a message between two avatars.
    
    This will need to be rafactored later. Ideally, Client objects will be
    (indirectly?) mapped by their avatar names once they select an avatar.
    """
    for c in self._clients.values():
      with c:
        if c.avatar and c.avatar.name == to:
          self._notifyw.send(c.notify, RecvMessage(from_, message))
          return True
    return False
  
  def avatar(self, name):
    """ Loads the avatar with the given name from the data source. """
    return Avatar(name)

if __name__ == "__main__":
  server = CombatServer()
  try:
    server.start("127.0.0.1", 10000, 10001)
  except KeyboardInterrupt:
    pass
