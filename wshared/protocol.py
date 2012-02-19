from yaml import load

from wproto.mapping import Mapping, normalize

def mapping(defn):
  return Mapping(normalize(load(open('protocol/'+defn+'.yml', 'r'))))