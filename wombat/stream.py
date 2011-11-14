from struct import pack, unpack
from threading import Lock

class Stream:
  """
  Wraps a connected socket for transmission translation as specified by send
  and receive protol descriptions.
  """
  def __init__(self, socket, send={}, recv={}):
    self.socket = socket
    self.setmapping(send, recv)
    self.lock = Lock()
  
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
    if op:
      opclass = self.recvmap.get(op, None)
      if opclass:
        return opclass() if opclass.SIMPLE else opclass.unpack(self)
      else:
        raise Exception("Invalid op code: {0}".format(op))
    else:
      return None
  
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
    rcv = self.socket.recv(length)
    if len(rcv) == length:
      return unpack('!{0}s'.format(length), rcv)
    else:
      return None
  
  def sendshort(self, short):
    return self.socket.send(pack('!H', short))
  
  def recvshort(self):
    rcv = self.socket.recv(2)
    if len(rcv) == 2:
      return unpack('!H', rcv)[0]
    else:
      return None
      
  def sendstring(self, string, encoding):
    byts = bytes(string, encoding)
    return self.socket.send(pack('!{0}s'.format(len(byts)), byts))
  
  def recvstring(self, bytelen, encoding):
    rcv = self.socket.recv(bytelen)
    if len(rcv) == bytelen:
      return unpack('!{0}s'.format(bytelen), rcv)[0].decode(encoding)
    else:
      return None
  