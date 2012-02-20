from struct import unpack as unpack, calcsize

def sock_unpack(fmt, socket):
  """ Unpacks network-endian data from a socket. """
  return unpack('!'+fmt, socket.recv(calcsize(fmt)))

def mergepacks(pack1, pack2):
  """ Merges two tuples of packing instructions into a single tuple """
  return tuple([pack1[0]+pack2[0]]+list(pack1[1:])+list(pack2[1:]))