from threading import Thread, Lock

from wproto.stream import Stream
from wproto.message import Message
from wshared.protocol import mapping


class GameClient:
  
  
  def __init__(self, action=None, response=None, notify=None):
    actmap = mapping('game_action')
    if action:
      actmap.extend(action)
    
    resmap = mapping('game_response')
    if response:
      resmap.extend(response)
    
    notmap = mapping('game_notify')
    if notify:
      notmap.extend(notify)
    
    self.control = Stream(send=actmap, recv=resmap)
    self.notify = Stream(recv=notmap)
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
    if key.istype('NotifyKey'):
      with self.controllock:
        res = self.control.sendrecv(Message('ClaimNotify', key=key.key))
      if res.istype('Success'):
        while 1:
          self.nhook(self.notify.recv())
      else:
        self.debug("Failed to claim notify connection.")
    else:
      self.debug("Failed to receive ClaimKey on notify connection.")
  
  
  def ndebug(self, n):
    self.debug("Received notification: {0}".format(n.__class__))
  
    
  def quit(self):
    with self.controllock:
      res = self.control.sendrecv(Message('Quit'))
      if res.istype('Success'):
        self.debug("Quit success.")
      else:
        self.debug("Quit failure.")
      return res

