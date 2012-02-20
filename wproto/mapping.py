from copy import deepcopy
from wproto.types import BASE_TYPES, unpack_short, pack_short
from wproto.packutils import mergepacks
from wproto.message import Message

class Mapping:
  def __init__(self, defs, types = BASE_TYPES):
    self.types = types
    self.defs = deepcopy(defs)
    self._inverse()
  
  def _inverse(self):
    self.codes = {}
    for code,cfg in self.defs.items():
      if 'type' in cfg:
        self.codes[cfg['type']] = code
  
  def code(self, type):
    return self.codes[type] if type in self.codes else None
  
  def type(self, code):
    return self.defs[code]['type'] if 'type' in self.defs[code] else None
  
  def extend(self, other):
    for code, cfg in other.defs.items():
      self.defs[code] = cfg
    self._inverse()
    self.types.update(other.types)
  
  def pack(self, message):
    op = self.code(message.type)
    if op in self.defs:
      pack = pack_short(op, {})
      for field in self.defs[op]['fields']:
        packfn = self.types[field['type']][0]
        pack = mergepacks(pack, packfn(message.get(field['name']), field['cfg']))
      return pack
    else:
      raise CodeError(op)
    
  def unpack(self, socket):
    op = unpack_short(socket, {})
    if op in self.defs:
      data = {}
      for field in self.defs[op]['fields']:
        unpackfn = self.types[field['type']][1]
        data[field['name']] = unpackfn(socket, field['cfg'])
      return Message(self.type(op), data)
    else:
      raise CodeError(op)


class CodeError(Exception):
  def __init__(self, code):
    self.code = code

# normalizes a protocol definition in an abbreviated format to a 
# consistent format accepted by Mapping(), and returns this normalized
# form. everything is deep-copied.
def normalize(defs):
  norm = {}
  for code, defn in defs.items():
    if isinstance(defn, dict):
      norm[code] = {'type': defn['type'], 'fields': []}
      if 'fields' in defn:
        for field in defn['fields']:
          if isinstance(field, dict):
            name, type = field['name'], field['type']
            cfg = field['cfg'] if 'cfg' in field else {}
            norm[code]['fields'].append({'name': name, 'type': type, 'cfg': cfg})
          else:
            name, type, *rest = field.split(' ')
            cfg = {'length': int(rest[0])} if len(rest) else {}
            norm[code]['fields'].append({
              'name': name, 'type': type, 'cfg': cfg
            })
    else:
      norm[code] = {'type': str(defn), 'fields': []}
  return norm
