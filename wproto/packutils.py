from struct import unpack

# authority: http://docs.python.org/library/struct.html
FMT_SIZE = {
  'c': 1,
  'b': 1,
  'B': 1,
  'h': 2,
  'H': 2,
  'i': 4,
  'I': 4,
  'l': 4,
  'L': 4,
  'q': 8,
  'Q': 8,
  'f': 4,
  'd': 8
}

def recvbytes(socket, n):
  return unpack('!{0}s'.format(n), socket.recv(n))[0]

def recvdata(socket, fmt):
  """ Receievs CONSTANT LENGTH data from a network socket. """
  return unpack('!'+fmt, socket.recv(FMT_SIZE[fmt]))[0]

def recvnstr(socket, nfmt='H', strenc='UTF-8'):
  """ Receive a variable-length encoded string from a network socket. """
  blen = recvdata(socket, nfmt)
  return recvbytes(socket, blen).decode(strenc)

def prepack(*args, intfmt='i', strenc='UTF-8', strlenfmt='H'):
  """
  Convenience method for packing several pieces of data. Returns a tuple
  consisting of a pack format string followed by data to be packed with that
  string. DOES NOT DEAL WITH ENDIANNESS, specify endianness in the actual call
  to struct.pack!
  
  PTYPE       Default Packing Scheme
   int         32-bit signed int
   str         16-bit unsigned bytelength N followed by N bytes representing
               a string encoded as UTF-8
   bytes       left as-is
   (str, x)    x (anything) packed with the struct packing format given by str
  See documentation on struct module for non-default format identifiers.
  """
  data = ['']
  for d in args:
    t = type(d)
    if t == int:
      data[0] += intfmt
      data.append(d)
    elif t == str:
      b = bytes(d, strenc)
      bl = len(b)
      data[0] += '{0}{1}s'.format(strlenfmt, bl)
      data.append(bl)
      data.append(b)
    elif t == bytes:
      bl = len(d)
      data[0] += '{0}s'.format(bl)
      data.append(d)
    elif t == tuple:
      fmt, x = data
      data[0] += fmt
      data.append(x)
    else:
      raise Exception("Cannot prepare unrecognized type for packing: {0}".format(t))
  return data


def mergepack(pack1, pack2):
  """ Appends a tuples of pre-packed data. """
  return tuple(pack1[0] + pack2[0]) + pack1[1:] + pack2[1:]

