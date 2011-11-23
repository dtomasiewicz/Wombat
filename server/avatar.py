from combatserver.datamodel import Model

class Avatar(Model):
  """ Avatars are player-controlled Units. """
  SCHEMA = ('id', 'name')
  TABLE = 'avatar'
  
  def _init(self):
    self.client = None
