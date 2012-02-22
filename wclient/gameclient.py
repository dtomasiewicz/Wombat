try:
  from select import epoll as poll, EPOLLIN as POLLIN
except:
  # for non-linux, use standard python polling object
  from select import poll, POLLIN
from collections import deque
  
from wproto.stream import Stream
from wproto.message import Message
from wshared.protocol import mapping


class GameClient:
  
  
  def __init__(self, action=None, response=None, notify=None):
    amap = mapping('game_action')
    if action:
      amap.extend(action)
    
    rmap = mapping('game_response')
    if response:
      rmap.extend(response)
    
    nmap = mapping('game_notify')
    if notify:
      nmap.extend(notify)
    
    self.control = Stream(send=amap, recv=rmap)
    self.notify = Stream(recv=nmap)
    self._handlers = deque()
    self._poll = poll()
    
    self.debugs = []
    self.nhook = self.ndebug
    
    self.destroyed = False
  
  
  def update(self):
    poll = self._poll.poll(0)
    while len(poll) > 0:
      
      for fileno, event in poll:
        self._poll.unregister(fileno)
        if fileno == self.control.fileno():
          res = self.control.recv()
          handler = self._handlers.popleft()
          if handler:
            handler(res)
        elif fileno == self.notify.fileno():
          notify = self.notify.recv()
          if notify.istype('NotifyKey'):
            self.control.send(Message('ClaimNotify', key=notify.key))
            self._handlers.append(self.hclaimnotify)
          else:
            self.nhook(notify)
        else:
          raise Exception("Unexpected polling object")
        
        if self.destroyed:
          break
        else:
          self._poll.register(fileno, POLLIN)
      
      if self.destroyed:
        break
      else:
        poll = self._poll.poll(0)
  
  
  def hclaimnotify(self, res):
    if res.istype('Success'):
      self.debug('Notify connection claimed successfully.')
    else:
      self.debug('Failed to claim notify connection: {0}'.format(res))
    
    
  def debug(self, msg):
    self.debugs.append(msg)
  
  
  def start(self, host, cport, nport):
    self.control.connect(host, cport)
    self._poll.register(self.control.fileno(), POLLIN)
    self.notify.connect(host, nport)
    self._poll.register(self.notify.fileno(), POLLIN)
  
  
  def destroy(self):
    self.destroyed = True
    self.control.close()
    self.notify.close()
    
  
  def ndebug(self, n):
    self.debug("Notification: {0}".format(n.__class__))
  
    
  def quit(self, handler):
    self.control.send(Message('Quit'))
    self._handlers.append(handler)
