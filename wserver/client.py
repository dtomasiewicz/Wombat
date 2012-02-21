class Client:
  """ Represents a single client application connected to the server. """
  
  def __init__(self, realm, control):
    self.realm = realm
    self.control = control
    self.world = None
    self.notify = None
    self.avatar = None
    self.unit = None
  
  def fileno(self):
    return self.control.fileno()
  
  def identity(self):
    """
    String identifying the client. Unique at the moment it is returned, but
    not guaranteed to be unique for the lifetime of the application.
    """
    return "{0}".format(id(self))
  
  def debug(self, msg):
    """ Sends client-relevant debugging info to the server. """
    self.realm.debug("CLI[{0}]: {1}".format(self.identity(), msg))
