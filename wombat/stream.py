from time import time
from struct import pack, unpack
from socket import error

from wombat.message import CodeError
from wombat.packutils import recvintus

class Stream:
  """
  Wraps a connected socket for transmission translation as specified by send
  and receive protol descriptions.
  """
  def __init__(self, send={}, recv={}):
    if send != None:
      # send map is inverted for class->opcode translation
      self.sendmap = dict((c,o) for o,c in send.items())
    if recv != None:
      self.recvmap = recv
  
  def send(self, socket, message):
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
    return socket.send(packed)
  
  def recv(self, socket):
    """
    Constructs a Message from bytes read in through the socket, based on the
    receive mapping.
    """
    op = recvintus(socket)
    opclass = self.recvmap.get(op, None)
    if opclass:
      return opclass() if opclass.SIMPLE else opclass.unpack(socket)
    else:
      raise CodeError(op)
  
  def sendrecv(self, socket, message):
    """
    Both sends a Message and receives a response Message, which is
    returned.
    """
    self.send(socket, message)
    return self.recv(socket)
