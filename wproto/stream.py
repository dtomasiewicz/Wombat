from time import time
from struct import pack, unpack
from socket import socket, error, AF_INET, SOCK_STREAM

from wproto.message import CodeError
from wproto.packutils import recvdata

class Stream:
  """
  Wraps a connected socket for transmission translation as specified by send
  and receive protol descriptions.
  """
  def __init__(self, sendmap, recvmap, sock=None, host=None, port=None):
    self.sendmap = sendmap
    self.recvmap = recvmap
    
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
  
  def close(self):
    self._socket.close()
    self.host = None
    self.port = None
  
  def send(self, message):
    """
    Translates a Message into bytes based on the send mapping and sends these 
    bytes over the socket.
    TODO: rewrite this for new type/map system
    """
    self.sendmap.send(message)
  
  def recv(self):
    """
    Constructs a Message from bytes read in through the socket, based on the
    receive mapping.
    TODO: rewrite this for new type/map system
    """
    return self.recvmap.recv(self._socket)
  
  def sendrecv(self, message):
    """
    Both sends a Message and receives a response Message, which is
    returned.
    TODO: rewrite this for new type/map system
    """
    self.send(message)
    return self.recv()
  
  def fileno(self):
    """ Allows the Stream object to be used with select(). """
    return self._socket.fileno()
