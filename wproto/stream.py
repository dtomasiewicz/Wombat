from time import time
from struct import pack
from socket import socket, error, AF_INET, SOCK_STREAM

class Stream:
  """
  Wraps a connected socket for transmission translation as specified by send
  and receive protol descriptions.
  """
  def __init__(self, send=None, recv=None, sock=None, host=None, port=None):
    self.sendmap = send
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
  
  def close(self):
    self._socket.close()
    self.host = None
    self.port = None
  
  def send(self, message):
    """
    Translates a Message into bytes based on the send mapping and sends these 
    bytes over the socket.
    """
    packed = self.sendmap.pack(message)
    self._socket.send(pack('!'+packed[0], *packed[1:]))
    
  
  def recv(self):
    """
    Constructs a Message from bytes read in through the socket, based on the
    receive mapping.
    """
    return self.recvmap.unpack(self._socket)
  
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
