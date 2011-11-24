#!/usr/bin/env python

from threading import Thread, Lock
from select import select, epoll, EPOLLIN
from socket import socket, AF_INET, SOCK_STREAM, error as socketerror
from struct import error as structerror
from time import time, sleep
from collections import deque
from random import randrange

from wproto.stream import Stream
from wproto.message import CodeError
from wshared.notify.mapping import NOTIFY_MAPPING
from wshared.notify.notification import *
from wshared.control.mapping import ACTION_MAPPING, RESPONSE_MAPPING

from wserver.reactor import Reactor, REALM, INSTANCE
from wserver.reaction.mapping import REACTION_MAPPING
from wserver.event import Event
from wserver.client import Client
from wserver.avatar import Avatar

class RealmServer:
  
  
  def __init__(self, data, srvcfg):
    self._data = data
    
    self._host = srvcfg['host']
    self._cport = int(srvcfg['control_port'])
    self._nport = int(srvcfg['notify_port'])
    self._backlog = int(srvcfg['backlog'])
    self._ntimeout = float(srvcfg['notify_timeout'])
    self._pollrate = float(srvcfg['poll_rate'])
    
    self.clients = set()
    
    # listener sockets for incoming control and notify connections
    self._clisten = socket(AF_INET, SOCK_STREAM)
    self._nlisten = socket(AF_INET, SOCK_STREAM)
    
    self._poll = epoll()
    # map of idle clients by their fileno. only protected by the GIL.
    self._idle = {}
    
    # list of read-only threads (must finish before queue is processed)
    self._rothreads = []
    
    # reaction queue
    self._queue = deque()
    self._qlock = Lock()
    
    # map of anonymous notify streams by their claim key
    self._anotifys = {}
    
    self._reactor = Reactor(REACTION_MAPPING)
    
    # map of cached avatars by their name
    self._avatars = {}
  
  
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
    
    self._poll.register(self._clisten, EPOLLIN)
    self._poll.register(self._nlisten, EPOLLIN)
    
    while 1:
      for fileno,event in self._poll.poll(self._pollrate):
        self._poll.unregister(fileno)
        if fileno == self._clisten.fileno():
          thread = Thread(target=self._caccept)
        elif fileno == self._nlisten.fileno():
          thread = Thread(target=self._naccept)
        else:
          client = self._idle.get(fileno)
          if client:
            del self._idle[fileno]
            thread = Thread(target=self._clientdata, args=[client])
          else:
            raise Exception("Unrecognized select: {0}".format(fd))
        self._rothreads.append(thread)
        thread.start()
      
      while len(self._rothreads):
        self._rothreads.pop().join()
      
      # all read-only threads are now finished
      self._processqueue()
    
  
  def queue(self, event):
    with self._qlock:
      self._queue.append(event)
  
  
  def addclient(self, client):
    self.clients.add(client)
    self.idleclient(client)
  
  
  def removeclient(self, client):
    self.clients.remove(client)
    client.realm = None
    client.control.close()
    client.control = None
    if client.notify:
      client.notify.close()
      client.notify = None
    if client.avatar:
      client.avatar.client = None
      client.avatar = None
  
  
  def addnotify(self, notify):
    key = randrange(65535) # this will need to be better in the future
    self._anotifys[key] = notify
    notify.send(NotifyKey(key))
  
  
  def idleclient(self, client):
    self._idle[client.fileno()] = client
    self._poll.register(client.fileno(), EPOLLIN)
  
  
  def claimnotify(self, key):
    """
    Claims an anonymous notify socket, returning and dereferencing it.
    """
    notify = self._anotifys.get(key)
    if notify:
      del self._anotifys[key]
      return notify
    else:
      return None
  
  
  def avatar(self, name):
    """ Returns the avatar with the given name, if it exists. """
    if not name in self._avatars:
      a = Avatar.first(self._data, name=name)
      if a:
        self._avatars[name] = a
    return self._avatars.get(name, None)
  
  
  def _processqueue(self):
    with self._qlock: # shouldn't really be necessary
      while len(self._queue):
        self._queue.popleft().process()


  def _clientdata(self, client):
    try:
      reaction = self._reactor.dispatch(client, client.control.recv())
    except (CodeError, socketerror, structerror) as e:
      if isinstance(e, CodeError):
        client.debug("Received invalid message code: {0}".format(e.code))
      elif isinstance(e, socketerror):
        client.debug("{0} occurred during message reception".format(errorcode[e.errno]))
      elif isinstance(e, structerror):
        client.debug("Failed to unpack message data")
      self.queue(Event(self.removeclient, client))
    else:
      res = None
      if reaction.DOMAIN is REALM:
        if reaction.READONLY:
          res = reaction.process()
        else:
          self.queue(reaction)
      elif reaction.DOMAIN is INSTANCE:
        if client.instance:
          if reaction.READONLY:
            res = reaction.process()
          else:
            client.instance.queue(reaction)
        else:
          res = InvalidAction()
      else:
        res = InvalidAction()
      
      # if we have a response already, send it and check for more data
      if res:
        client.debug("{0} => {1}".format(reaction.action, res))
        client.control.send(res)
        
        if len(select([client], [], [], 0)[0]) == 1:
          self._clientdata(client)
        else:
          self.idleclient(client)
      # else response was deferred for queue processing
  
  
  def _caccept(self):
    """ Connects a new client. """
    sock, (host, port) = self._clisten.accept()
    self._poll.register(self._clisten, EPOLLIN)
    sock.setblocking(0)
    
    client = Client(self, Stream(
        recv=ACTION_MAPPING, send=RESPONSE_MAPPING,
        sock=sock, host=host, port=port))
    
    self.queue(Event(self.addclient, client))
  
  
  def _naccept(self):
    """
    Accepts an incoming notify connection and adds it to the list of anonymous 
    notify streams, to later be claimed by a client. Sends the claim key to the
    client for this purpose.
    """
    sock, (host, port) = self._nlisten.accept()
    self._poll.register(self._nlisten, EPOLLIN)
    sock.setblocking(0)
    
    stream = Stream(send=NOTIFY_MAPPING, sock=sock, host=host, port=port)
    
    self.queue(Event(self.addnotify, stream))



if __name__ == "__main__":
  from argparse import ArgumentParser
  parser = ArgumentParser()
  parser.add_argument('configfile')
  args = parser.parse_args()
  
  from configparser import SafeConfigParser as ConfigParser
  config = ConfigParser()
  config.readfp(open(args.configfile))
  
  from postgresql import driver
  data = driver.connect(**dict(config.items('datasource')))
  server = RealmServer(data, dict(config.items('server')))
  try:
    server.start()
  except KeyboardInterrupt:
    pass
