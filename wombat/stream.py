from time import time
from struct import pack, unpack
from threading import Lock
from socket import error

from wombat.message import CodeError

class Stream:
  """
  Wraps a connected socket for transmission translation as specified by send
  and receive protol descriptions.
  """
  def __init__(self, socket, send={}, recv={}):
    self.socket = socket
    self.setmapping(send, recv)
    self.lock = Lock()
    self.created = time()
  
  def setmapping(self, send=None, recv=None):
    """ Sets the mapping (send and receive protocols) for this stream. """
    if send != None:
      # send map is inverted for class->opcode translation
      self.sendmap = dict((c,o) for o,c in send.items())
    if recv != None:
      self.recvmap = recv
  
  def send(self, message):
    """
    Translates a Message into bytes based on the send mapping and sends these 
    bytes over the socket.
    """
    if message.SIMPLE:
      fmt = ''
      data = []
    else:
      fmt, *data = message.pack()
    packed = pack('!H'+fmt, self.sendmap[message.__class__], *data)
    return self.socket.send(packed)
  
  def recv(self):
    """
    Constructs a Message from bytes read in through the socket, based on the
    receive mapping.
    """
    op = self.recvshort()
    opclass = self.recvmap.get(op, None)
    if opclass:
      return opclass() if opclass.SIMPLE else opclass.unpack(self)
    else:
      raise CodeError(op)
  
  def sendrecv(self, message):
    """
    Both sends a Message and receives a response Message, which is
    returned.
    """
    if self.send(message):
      return self.recv()
    else:
      return None
  
  def sendbytes(self, byts):
    blen = len(byts)
    return self.socket.send(pack('!{0}s'.format(blen), byts))
  
  def recvbytes(self, length):
    return unpack('!{0}s'.format(length), self.socket.recv(length))
  
  def sendshort(self, short):
    return self.socket.send(pack('!H', short))
  
  def recvshort(self):
    return unpack('!H', self.socket.recv(2))[0]
      
  def sendstring(self, string, encoding):
    byts = bytes(string, encoding)
    return self.socket.send(pack('!{0}s'.format(len(byts)), byts))
  
  def recvstring(self, bytelen, encoding):
    return unpack('!{0}s'.format(bytelen),
                  self.socket.recv(bytelen))[0].decode(encoding)
  