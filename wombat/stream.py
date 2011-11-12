from socket import socket, AF_INET, SOCK_STREAM
from struct import pack, unpack

class Stream:
  
  def __init__(self, socket=None, address=None, send=None, recv=None):
    self.socket = socket
    self.address = address
    self.setmapping(send, recv)
  
  def connect(self, host, port):
    self.socket = socket(AF_INET, SOCK_STREAM)
    return self.socket.connect((host, port))
    
  def listen(self, host, port, handler, backlog=5):
    self.socket = socket(AF_INET, SOCK_STREAM)
    self.socket.bind((host, port))
    self.socket.listen(backlog)
    while True:
      sock, addr = self.socket.accept()
      handler(Stream(socket=sock, address=addr))
  
  def setmapping(self, send=None, recv=None):
    if send != None:
      # send map is inverted for class->opcode translation
      self.send_mapping = dict((c,o) for o,c in send.items())
    if recv != None:
      self.recv_mapping = recv
  
  def close(self):
    r = self.socket.close()
    self.socket = None
    return r
  
  def recv(self):
    op = self.recvshort()
    if op:
      opclass = self.recv_mapping.get(op, None)
      if opclass:
        return opclass() if opclass.SIMPLE else opclass.unpack(self)
      else:
        raise Exception("Invalid op code: {0}".format(op))
    else:
      return None
  
  def send(self, message):
    if message.SIMPLE:
      fmt = ''
      data = []
    else:
      fmt, *data = message.pack()
    packed = pack('!H'+fmt, self.send_mapping[message.__class__], *data)
    return self.socket.send(packed)
  
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
  
  def recvshort(self):
    rcv = self.socket.recv(2)
    if len(rcv) == 2:
      return unpack('!H', rcv)[0]
    else:
      return None
  
  def recvstring(self, bytelen, encoding):
    rcv = self.socket.recv(bytelen)
    if len(rcv) == bytelen:
      return unpack('!{0}s'.format(bytelen), rcv)[0].decode(encoding)
    else:
      return None
  