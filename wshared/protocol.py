from os.path import dirname, join
from yaml import load

from wproto.mapping import Mapping


def mapping(defn):
  fname = join(dirname(__file__), 'protocol', defn+'.yml')
  return Mapping(normalize(load(open(fname, 'r'))))

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
