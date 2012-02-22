from struct import pack
from socket import socket, AF_INET, SOCK_STREAM

from wproto.mapping import Mapping

class Stream:
  """
  Wraps a socket for sending and receiving Message objects as specified in the
  given send/receive Mappings. 
  """
  
  def __init__(self, send=None, recv=None, sock=None, host=None, port=None):
    self.sendmap = send if send else Mapping()
    self.recvmap = recv if recv else Mapping()
    
    if sock:
      self._socket = sock
    else:
      self._socket = socket(AF_INET, SOCK_STREAM)
    
    self.host = host
    self.port = port
  
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
  
  
  def fileno(self):
    """ Allows the Stream object to be used with select(). """
    return self._socket.fileno()
  
  
  def setblocking(self, blocking):
    self._socket.setblocking(1 if blocking else 0)
    
  def getblocking(self):
    return self._socket.gettimeout() == None
