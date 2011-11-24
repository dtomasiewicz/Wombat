from socket import socket, AF_INET, SOCK_STREAM
from select import epoll, EPOLLIN
from threading import Thread, Lock
from collections import deque
from random import randrange

from wproto.stream import Stream
from wshared.control.mapping import ACTION_MAPPING, RESPONSE_MAPPING
from wshared.notify.mapping import NOTIFY_MAPPING
from wshared.notify.notification import NotifyKey

from wserver.reactor import Reactor
from wserver.react.mapping import REACTION_MAPPING
from wserver.client import Client
from wserver.event import Event


def extend_map(m1, m2):
  new = m1.copy()
  new.update(m2)
  return new


class GameServer:
  """
  Base server class. Accepts control/notify connections, manages a list of
  clients, and receives instructions from clients.
  """
  
  
  def __init__(self, action={}, response={}, notify={}, react={}):
    self._action = extend_map(ACTION_MAPPING, action)
    self._response = extend_map(RESPONSE_MAPPING, response)
    self._notify = extend_map(NOTIFY_MAPPING, notify)
    
    self._reactor = Reactor(extend_map(REACTION_MAPPING, react))
    self._queue = deque()
    self._qlock = Lock()
    
    self._clisten = socket(AF_INET, SOCK_STREAM)
    self._nlisten = socket(AF_INET, SOCK_STREAM)
    self._poll = epoll()
    self._clients = set()
    self._idle = {} # map of idle clients by their fileno
    self._anotifys = {} # map of anonymous notify sockets by their claim key
  
  
  def debug(self, message):
    print(message)
    
  
  def start(self, host='127.0.0.1', cport=10000, nport=10001, backlog=5,
            ntimeout=5, pollrate=.001):
    self.host = host
    self.cport = cport
    self.nport = nport
    
    # listens for incoming control connections
    self._clisten.bind((host, cport))
    self._clisten.setblocking(0)
    self._clisten.listen(backlog)
    
    # listens for incoming notify connections
    self._nlisten.bind((host, nport))
    self._nlisten.setblocking(0)
    self._nlisten.listen(backlog)
    
    self._poll.register(self._clisten.fileno(), EPOLLIN)
    self._poll.register(self._nlisten.fileno(), EPOLLIN)
    
    while 1:
      waitfor = []
      for fileno, event in self._poll.poll(pollrate):
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
        waitfor.append(thread)
        thread.start()
      
      while len(waitfor):
        waitfor.pop().join()
      
      # all wait threads finished; process queue synchronously
      self._processqueue()
  
  
  def queue(self, event):
    with self._qlock:
      self._queue.append(event)
  
  
  def addclient(self, client):
    self._clients.add(client)
    self.idleclient(client)
  
  
  def removeclient(self, client):
    self._clients.remove(client)
    client.realm = None
    client.control.close()
    client.control = None
    if client.notify:
      client.notify.close()
      client.notify = None
  
  
  def idleclient(self, client):
    self._idle[client.fileno()] = client
    self._poll.register(client.fileno(), EPOLLIN)
  
  
  def addnotify(self, notify):
    key = randrange(65535) # this will need to be better in the future
    self._anotifys[key] = notify
    notify.send(NotifyKey(key))
  
  
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
  
  
  def _processqueue(self):
    with self._qlock:
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
      if reaction.READONLY:
        reaction.process()
      else:
        self.queue(reaction)
  
  
  def _caccept(self):
    """ Connects a new client. """
    sock, (host, port) = self._clisten.accept()
    self._poll.register(self._clisten, EPOLLIN)
    sock.setblocking(0)
    
    client = Client(self, Stream(recv=self._action, send=self._response,
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
    
    stream = Stream(send=self._notify, sock=sock, host=host, port=port)
    
    self.queue(Event(self.addnotify, stream))
