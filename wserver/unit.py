from wserver.datamodel import Model

class Unit(Model):
  TABLE = 'unit'
  SCHEMA = {
    'id'         : {'type': int},
    'name'       : {'type': str,   'default': 'Unknown'},
    'key'        : {'type': bytes, 'default': b'\0'*32}
  }
  PRIMARY_KEY = 'id'
  
  def _init(self):
    self.client = None
