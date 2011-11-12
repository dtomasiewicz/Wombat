#!/usr/bin/env python
#
# Runs a combat server

from random import randrange
from wombat.stream import Stream
from wombat.control.mapping import RESPONSE_MAPPING, ACTION_MAPPING
from wombat.control.action import Identify
from wombat.control.response import RemapNotify, InvalidAction, InvalidIdentity
from wombat.notify.mapping import NOTIFY_MAPPING
from client import Client
from threading import Thread

class CombatServer:
  def __init__(self):
    self.clients = {}
  
  def start(self, host, cport, nport):
    # listen for incoming notify connections
    self.nlisten = Stream()
    Thread(target=self.nlisten.listen, args=(host, nport, self.naccept)).start()
    
    # listen for incoming control connections
    self.clisten = Stream()
    self.clisten.listen(host, cport, self.caccept) #todo change backlog
    
  def caccept(self, control):
    control.setmapping(send=RESPONSE_MAPPING, recv=ACTION_MAPPING)
    Thread(target=self.spawnclient, args=(control,)).start()
  
  def spawnclient(self, control):
    while 1:
      identity = randrange(65535) # max short value
      if not self.clients.get(identity, None):
        break
    
    self.clients[identity] = client = Client(self, identity, control)
    client.start()
    # client is disconnected; clean up
    del self.clients[identity]
    client.control.close()
    if client.notify:
      client.notify.close()
  
  def naccept(self, notify):
    notify.setmapping(send=RESPONSE_MAPPING, recv=ACTION_MAPPING)
    Thread(target=self.matchnotify, args=(notify,)).start()
  
  def matchnotify(self, notify):
    act = notify.recv()
    if act.istype(Identify):
      client = self.clients.get(act.clientid, None)
      if client:
        notify.send(RemapNotify())
        notify.setmapping(send=NOTIFY_MAPPING,recv={})
        client.notify = notify
      else:
        stream.send(InvalidIdentity())
        stream.close()
    else:
      stream.send(InvalidAction())
      stream.close()
    
  

if __name__ == "__main__":
  CombatServer().start("127.0.0.1", 10000, 10001)