from struct import pack, unpack

# wraps a connected socket for communication with the given send/recv protocols
class Stream:
  
  def __init__(self, socket, send={}, recv={}):
    self.socket = socket
    self.setmapping(send, recv)
  
  def setmapping(self, send=None, recv=None):
    if send != None:
      # send map is inverted for class->opcode translation
      self.sendmap = dict((c,o) for o,c in send.items())
    if recv != None:
      self.recvmap = recv
  
  def send(self, message):
    if message.SIMPLE:
      fmt = ''
      data = []
    else:
      fmt, *data = message.pack()
    packed = pack('!H'+fmt, self.sendmap[message.__class__], *data)
    return self.socket.send(packed)
  
  def recv(self):
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
  