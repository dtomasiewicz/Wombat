from socket import inet_ntoa, inet_aton

from wproto.packutils import sock_unpack, mergepacks

# 32-bit integer
def pack_int(data, cfg):
  fmt = 'I' if 'signed' in cfg and cfg['signed'] else 'i'
  return (fmt, data)

def unpack_int(socket, cfg):
  fmt = 'I' if 'signed' in cfg and cfg['signed'] else 'i'
  return sock_unpack(fmt, socket)[0]

# 16-bit integer
def pack_short(data, cfg):
  fmt = 'H' if 'signed' in cfg and cfg['signed'] else 'h'
  return (fmt, data)

def unpack_short(socket, cfg):
  fmt = 'H' if 'signed' in cfg and cfg['signed'] else 'h'
  return sock_unpack(fmt, socket)[0]

# 64-bit integer
def pack_long(data, cfg):
  fmt = 'Q' if 'signed' in cfg and cfg['signed'] else 'q'
  return (fmt, data)

def unpack_long(socket, cfg):
  fmt = 'Q' if 'signed' in cfg and cfg['signed'] else 'q'
  return sock_unpack(fmt, socket)[0]

# bytestring
def pack_bytes(data, cfg):
  if 'length' in cfg:
    return (str(cfg['length'])+'s', data)
  else:
    raise Exception('<bytes> field must have a configured length')

def unpack_bytes(socket, cfg):
  if 'length' in cfg:
    return sock_unpack(str(cfg['length'])+'s', socket)[0]
  else:
    raise Exception('<bytes> field must have a configured length')

# fixed-length string
def pack_str(data, cfg):
  if 'length' in cfg:
    enc = cfg['encoding'] if 'encoding' in cfg else 'ASCII'
    return (str(cfg['length'])+'s', bytes(data, enc))
  else:
    raise Exception('<bytes> field must have a configured length')

def unpack_str(socket, cfg):
  if 'length' in cfg:
    enc = cfg['encoding'] if 'encoding' in cfg else 'ASCII'
    return sock_unpack(str(cfg['length'])+'s', socket)[0].decode(enc)
  else:
    raise Exception('<bytes> field must have a configured length')

# variable-length string
def pack_nstr(data, cfg):
  if 'nformat' in cfg:
    nfmt = cfg['nformat']
    enc = cfg['encoding'] if 'encoding' in cfg else 'UTF-8'
    strbytes = bytes(data, enc)
    l = len(strbytes)
    return (nfmt+str(l)+'s', l, strbytes)
  else:
    raise Exception('<nstr> field must have a configured nformat')

def unpack_nstr(socket, cfg):
  if 'nformat' in cfg:
    nfmt = cfg['nformat']
    enc = cfg['encoding'] if 'encoding' in cfg else 'UTF-8'
    l = sock_unpack(nfmt, socket)[0]
    return sock_unpack(str(l)+'s', socket)[0].decode(enc)
  else:
    raise Exception('<nstr> field must have a configured nformat')

# variable-length string - nformat=i
def pack_istr(data, cfg):
  scfg = cfg.copy()
  scfg['nformat'] = 'i'
  return pack_nstr(data, scfg)

def unpack_istr(data, cfg):
  scfg = cfg.copy()
  scfg['nformat'] = 'i'
  return unpack_nstr(data, scfg)

# variable-length string - nformat=h
def pack_sstr(data, cfg):
  scfg = cfg.copy()
  scfg['nformat'] = 'h'
  return pack_nstr(data, scfg)

def unpack_sstr(data, cfg):
  scfg = cfg.copy()
  scfg['nformat'] = 'h'
  return unpack_nstr(data, scfg)

# variable-length string - nformat=q
def pack_lstr(data, cfg):
  scfg = cfg.copy()
  scfg['nformat'] = 'q'
  return pack_nstr(data, scfg)

def unpack_lstr(data, cfg):
  scfg = cfg.copy()
  scfg['nformat'] = 'q'
  return unpack_nstr(data, scfg)

# fixed-length list
def pack_list(data, cfg):
  if 'length' in cfg and 'etype' in cfg:
    epack, eunpack = cfg['etype']
    ecfg = cfg['ecfg'] if 'ecfg' in cfg else {}
    
    pack = [""]
    for i in range(cfg['length']):
      efmt, *edata = epack(data[i], ecfg)
      pack[0] += efmt
      pack.extend(edata)
    return tuple(pack)
  else:
    raise Exception('<list> field must have a configured length, etype')
  
def unpack_list(socket, cfg):
  if 'length' in cfg and 'etype' in cfg:
    epack, eunpack = cfg['etype']
    ecfg = cfg['ecfg'] if 'ecfg' in cfg else {}
    return (eunpack(socket, ecfg) for _ in range(cfg['length']))
  else:
    raise Exception('<list> field must have a configured length, etype')

# variable-length list
def pack_nlist(data, cfg):
  if 'nformat' in cfg:
    lcfg = cfg.copy()
    lcfg['length'] = len(data)
    return mergepacks([cfg['nformat'], data], pack_list(data, lcfg))
  else:
    raise Exception('<nlist> field must have a configured nformat')
  
def unpack_nlist(socket, cfg):
  if 'nformat' in cfg:
    lcfg = cfg.copy()
    lcfg['length'] = sock_unpack(cfg['nformat'], socket)[0]
    return unpack_list(socket, lcfg)
  else:
    raise Exception('<nlist> field must have a configured nformat')

# variable-length list - nformat=i
def pack_ilist(data, cfg):
  lcfg = cfg.copy()
  lcfg['nformat'] = 'i';
  return pack_nlist(data, lcfg)

def unpack_ilist(data, cfg):
  lcfg = cfg.copy()
  lcfg['nformat'] = 'i';
  return unpack_nlist(data, lcfg)

# variable-length list - nformat=s
def pack_slist(data, cfg):
  lcfg = cfg.copy()
  lcfg['nformat'] = 's';
  return pack_nlist(data, lcfg)

def unpack_slist(data, cfg):
  lcfg = cfg.copy()
  lcfg['nformat'] = 's';
  return unpack_nlist(data, lcfg)

# variable-length list - nformat=l
def pack_llist(data, cfg):
  lcfg = cfg.copy()
  lcfg['nformat'] = 'l';
  return pack_nlist(data, lcfg)

def unpack_llist(data, cfg):
  lcfg = cfg.copy()
  lcfg['nformat'] = 'l';
  return unpack_nlist(data, lcfg)

# IPv4 address
def pack_ipv4(data, cfg):
  return ('4s', inet_aton(data))
  
def unpack_ipv4(socket, cfg):
  return inet_ntoa(sock_unpack('4s', socket)[0])


BASE_TYPES = {
  'int': (pack_int, unpack_int),
  'short': (pack_short, unpack_short),
  'long': (pack_long, unpack_long),
  'bytes': (pack_bytes, unpack_bytes),
  'str': (pack_str, unpack_str),
  'nstr': (pack_nstr, unpack_nstr),
  'istr': (pack_istr, unpack_istr),
  'sstr': (pack_sstr, unpack_sstr),
  'lstr': (pack_lstr, unpack_lstr),
  'list': (pack_list, unpack_list),
  'nlist': (pack_list, unpack_list),
  'ilist': (pack_list, unpack_list),
  'slist': (pack_list, unpack_list),
  'llist': (pack_list, unpack_list),
  'ipv4': (pack_ipv4, unpack_ipv4)
}