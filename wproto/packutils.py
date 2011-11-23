from struct import unpack

def recvint(socket):
  return unpack('!i', socket.recv(4))[0]

def recvintu(socket):
  return unpack('!I', socket.recv(4))[0]
  
def recvintus(socket):
  return unpack('!H', socket.recv(2))[0]

def recvstring(socket, bytelen=None, lenfunc=recvintus, strenc='UTF-8'):
  bytelen = lenfunc(socket)
  return unpack('!{0}s'.format(bytelen), socket.recv(bytelen))[0].decode(strenc)

def prepack(*args, intfmt='H', strenc='UTF-8'):
  data = ['']
  for i in range(len(args)):
    t = type(args[i])
    if t == int:
      data[0] += intfmt
      data.append(args[i])
    elif t == str:
      b = bytes(args[i], strenc)
      bl = len(b)
      data[0] += 'H{0}s'.format(bl)
      data.append(bl)
      data.append(b)
    else:
      raise Exception("Cannot prepare unrecognized type for packing: {0}".format(t))
  return data