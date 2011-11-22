from time import time
from struct import pack, unpack
from socket import socket, error, AF_INET, SOCK_STREAM

from wombat.message import CodeError
from wombat.packutils import recvintus

class Stream:
  """
  Wraps a connected socket for transmission translation as specified by send
  and receive protol descriptions.
  """
  def __init__(self, send={}, recv={}, sock=None, host=None, port=None):
    # send map is inverted for class->opcode translation
    self.sendmap = dict((c,o) for o,c in send.items())
    self.recvmap = recv
    
    if sock:
      self._socket = sock
    else:
      self._socket = socket(AF_INET, SOCK_STREAM)
    
    self.host = host
    self.port = port
    self.last_send = None
    self.last_recv = None
  
  def connect(self, host, port):
    self._socket.connect((host, port))
    self.host = host
    self.port = port
  
  def close(self, ):
    self._socket.close()
    self.host = None
    self.port = None
  
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
    self.last_send = time()
    return self._socket.send(packed)
  
  def recv(self):
    """
    Constructs a Message from bytes read in through the socket, based on the
    receive mapping.
    """
    op = recvintus(self._socket)
    opclass = self.recvmap.get(op, None)
    if opclass:
      self.last_recv = time()
      return opclass() if opclass.SIMPLE else opclass.unpack(self._socket)
    else:
      raise CodeError(op)
  
  def sendrecv(self, message):
    """
    Both sends a Message and receives a response Message, which is
    returned.
    """
    self.send(message)
    return self.recv()
  
  def fileno(self):
    return self._socket.fileno()
