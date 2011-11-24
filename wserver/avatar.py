from wserver.datamodel import Model

class Avatar(Model):
  """
  An Avatar represents a character controlled by a player. Since Avatars exist
  at the Realm level, each has its own Unit at the Instance level. This allows
  two Avatars on any single realm to communicate regardless of which Instance
  their associated Units are in.
  """
  SCHEMA = ('id', 'name')
  TABLE = 'avatar'
  
  def _init(self):
    self.client = None
