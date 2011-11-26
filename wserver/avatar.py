from wserver.datamodel import Model

class Avatar(Model):
  """
  An Avatar represents a character controlled by a player. Since Avatars exist
  at the Realm level, each has its own Unit at the World level. This allows
  two Avatars on any single realm to communicate regardless of which World
  their associated Units are in.
  """
  TABLE = 'avatar'
  SCHEMA = {
    'id'         : {'type': int},
    'name'       : {'type': str,   'default': 'Unknown'},
    'world_id'   : {'type': int,  'default': 0},
    'world_unit' : {'type': int,   'default': 0},
    'world_key'  : {'type': bytes, 'default': b'\0'*32}
  }
  PRIMARY_KEY = 'id'
  
  def _init(self):
    self.client = None

  def worldinfo(self):
    return (self.world_id, self.world_unit, self.world_key)
