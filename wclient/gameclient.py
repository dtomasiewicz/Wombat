from threading import Thread, Lock

from wproto.stream import Stream

from wshared.control.game import *
from wshared.notify.game import *


def extend_map(m1, m2):
  new = m1.copy()
  new.update(m2)
  return new


class GameClient:
  
  
  def __init__(self, action={}, response={}, notify={}):
    self.control = Stream(send=extend_map(GAME_ACTION, action),
                          recv=extend_map(GAME_RESPONSE, response))
    self.notify = Stream(recv=extend_map(GAME_NOTIFY, notify))
    self.controllock = Lock()
    self.debugs = []
    self.nhook = self.ndebug
  
  
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
      with self.controllock:
        res = self.control.sendrecv(ClaimNotify(key.key))
      if res.SUCCESS:
        while 1:
          self.nhook(self.notify.recv())
      else:
        self.debug("Failed to claim notify connection.")
    else:
      self.debug("Failed to receive ClaimKey on notify connection.")
  
  
  def ndebug():
    self.debug("Received notification: {0}".format(n.__class__))
  
    
  def quit(self):
    with self.controllock:
      res = self.control.sendrecv(Quit())
      if res.SUCCESS:
        self.debug("Quit success.")
      else:
        self.debug("Quit failure.")
      return res

