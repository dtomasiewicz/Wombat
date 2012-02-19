from copy import deepcopy
from wproto.types import BASE_TYPES, unpack_short, pack_short
from wproto.packutils import mergepacks

class Mapping:
  def __init__(self, defs, types = BASE_TYPES):
    self.types = types
    self.defs = deepcopy(defs)
    self._inverse()
  
  def _inverse(self):
    self.codes = {}
    for code,cfg in self.defs.items():
      if 'alias' in cfg:
        self.codes[cfg['alias']] = code
  
  def code(self, alias):
    return self.codes[alias] if alias in self.codes else None
  
  def alias(self, code):
    return self.defs[code]['alias'] if 'alias' in self.defs[code] else None
  
  def extend(self, other):
    for code, cfg in other.defs.items():
      self.defs[code] = cfg
    self._inverse()
    self.types.update(other.types)
  
  def pack(self, message):
    op = self.code(message.alias)
    if op in self.defs:
      pack = pack_short(op, {})
      for field in self.defs[op].fields:
        packfn = self.types[field['type']][0]
        pack = mergepacks(pack, packfn(message.get(field['name']), field['cfg']))
      return pack
    else:
      raise CodeError(op)
    
  def unpack(self, socket):
    op = unpack_short(socket, {})
    if op in self.defs:
      data = {}
      for field in self.defs[op].fields:
        unpackfn = self.types[field['type']][1]
        data[field['name']] = unpackfn(socket, field['cfg'])
      return Message(self.alias(op), data)
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
      norm[code] = {'alias': defn['alias'], 'fields': []}
      if 'fields' in defn:
        for field in defn['fields']:
          if isinstance(field, dict):
            name, type = field['name'], field['type']
            cfg = field['cfg'] if 'cfg' in field else {}
            norm[code]['fields'].append({'name': name, 'type': type, 'cfg': cfg})
          else:
            name, type, length = field.split(' ')
            norm[code]['fields'].append({
              'name': name, 'type': type, 'cfg': {'length': length}
            })
    else:
      norm[code] = {'alias': str(defn), 'fields': []}
  return norm
