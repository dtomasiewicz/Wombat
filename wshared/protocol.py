from os.path import dirname, join
from yaml import load

from wproto.mapping import Mapping, normalize

def mapping(defn):
  fname = join(dirname(__file__), 'protocol', defn+'.yml')
  return Mapping(normalize(load(open(fname, 'r'))))