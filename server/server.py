#!/usr/bin/env python

from threading import Thread, Lock
from select import select
from socket import socket, AF_INET, SOCK_STREAM
from random import randrange
from time import time, sleep

from wombat.stream import Stream
from wombat.notify.mapping import NOTIFY_MAPPING
from wombat.notify.notification import *
from wombat.control.mapping import ACTION_MAPPING, RESPONSE_MAPPING
from wombat.control.action import ClaimNotify
from wombat.control.response import Success, InvalidNotifyKey

from combatserver.client import Client
from combatserver.avatar import Avatar
from data.source import Source

class CombatServer:
  
  def __init__(self, srvcfg, datacfg):
    self._host = srvcfg['host']
    self._cport = int(srvcfg['control_port'])
    self._nport = int(srvcfg['notify_port'])
    self._backlog = int(srvcfg['backlog'])
    self._ntimeout = float(srvcfg['notify_timeout'])
    self._pollrate = float(srvcfg['poll_rate'])
    
    # listener sockets for incoming control and notify connections
    self._clisten = socket(AF_INET, SOCK_STREAM)
    self._nlisten = socket(AF_INET, SOCK_STREAM)
    
    self._clients = set()
    self._idle = set() # idle sockets to be polled by select()
    
    self._avatars = {} # map of (loaded) avatars by name
    self._avatarslock = Lock()
    
    # map of anonymous notify streams by their claim key
    self._anotifys = {}
    self._anotifyslock = Lock()
    
    self._data = Source(datacfg)
  
  def debug(self, message):
    print(message)
  
  def start(self):
    # listens for incoming control connections
    self._clisten.bind((self._host, self._cport))
    self._clisten.setblocking(0)
    self._clisten.listen(self._backlog)
    
    # listens for incoming notify connections
    self._nlisten.bind((self._host, self._nport))
    self._nlisten.setblocking(0)
    self._nlisten.listen(self._backlog)
    
    # set of idle connections to be select()ed from
    self._idle = set((self._clisten, self._nlisten))
    
    # cleanup daemon for unclaimed notify threads
    cleanup = Thread(target=self.cleanup)
    cleanup.daemon = True
    cleanup.start()
    
    while 1:
      if len(self._idle):
        for ready in select(self._idle, [], [], self._pollrate)[0]:
          self._idle.remove(ready)
          if isinstance(ready, Client):
            Thread(target=self._clientdata, args=[ready]).start()
          elif ready == self._clisten:
            Thread(target=self._caccept).start()
          elif ready == self._nlisten:
            Thread(target=self._naccept).start()
          else:
            self.debug("Unrecognized select: {0}".format(ready))
      elif self._pollrate > 0:
        sleep(self._pollrate)
  
  def _clientdata(self, client):
    while client.state:
      try:
        action = client.control.recv()
      except BaseException as e:
        if isinstance(e, CodeError):
          self.debug("Received invalid message code: {0}".format(e.code))
        elif isinstance(e, socketerror):
          self.debug("{0} occurred during message reception".format(errorcode[e.errno]))
        elif isinstance(e, structerror):
          self.debug("Failed to unpack message data")
        client.state = None
      else:
        with client:
          start = time()
          # notify connection can be claimed at any time
          if isinstance(action, ClaimNotify):
            client.notify = self.claimnotify(action.key)
            if client.notify:
              res = Success()
            else:
              res = InvalidNotifyKey()
          else:
            res = client.state(action)
          ms = (time()-start)*1000
          
          client.debug("{0} => {1} in {2:.2f} ms".format(action, res, ms))
        client.control.send(res)
        
        # only continue processing if more data on socket
        if len(select([client], [], [], 0)[0]) == 0:
          break
    
    if not client.state:
      self._disconnect(client)
    else:
      self._idle.add(client)
  
  
  def cleanup(self):
    """
    Closes notify connections that have not been claimed after NOTIFY_TIMEOUT 
    seconds.
    """
    while 1:
      for key, notify in tuple(self._anotifys.items()):
        if notify.last_send > time()+self._ntimeout:
          with self._anotifyslock:
            # make sure it wasn't claimed while waiting for lock
            if key in self._anotifys:
              del self._anotifys[key]
              notify.close()
      sleep(5)
  
  def claimnotify(self, key):
    """
    Claims an anonymous notify socket, returning and dereferencing it.
    """
    with self._anotifyslock:
      notify = self._anotifys.get(key)
      if notify:
        del self._anotifys[key]
        return notify
      else:
        return None
  
  def _caccept(self):
    """ Connects a new client. """
    sock, (host, port) = self._clisten.accept()
    self._idle.add(self._clisten)
    sock.setblocking(0)
    
    client = Client(self, Stream(
        recv=ACTION_MAPPING, send=RESPONSE_MAPPING,
        sock=sock, host=host, port=port))
    
    self._clients.add(client)
    client.debug("Connected")
    self._idle.add(client)
  
  def _naccept(self):
    """
    Accepts an incoming notify connection and adds it to the list of anonymous 
    notify streams, to later be claimed by a client. Sends the claim key to the
    client for this purpose.
    """
    sock, (host, port) = self._nlisten.accept()
    self._idle.add(self._nlisten)
    sock.setblocking(0)
    
    stream = Stream(send=NOTIFY_MAPPING, sock=sock, host=host, port=port)
    
    key = randrange(65535) # this will need to be more secure in the future
    self._anotifys[key] = stream
    stream.send(NotifyKey(key))
  
  def _disconnect(self, client):
    """ Disconnects a client. """
    self._clients.remove(client)
    with client:
      client.control.close()
      if client.notify:
        client.notify.close()
      if client.avatar:
        with client.avatar:
          client.avatar.setclient(None)
  
  def avatar(self, name):
    """ Returns the avatar with the given name, if it exists. """
    a = self._avatars.get(name)
    if not a:
      a = Avatar.first(self._data, name=name)
      if a:
        with self._avatarslock:
          # make sure it wasn't loaded by another thread while waiting for lock
          if not name in self._avatars:
            self._avatars[name] = a
    return a

if __name__ == "__main__":
  from argparse import ArgumentParser
  parser = ArgumentParser()
  parser.add_argument('configfile')
  args = parser.parse_args()
  
  from configparser import SafeConfigParser as ConfigParser
  config = ConfigParser()
  config.readfp(open(args.configfile))
  
  server = CombatServer(
      dict(config.items('server')), dict(config.items('datasource')))
  try:
    server.start()
  except KeyboardInterrupt:
    pass
