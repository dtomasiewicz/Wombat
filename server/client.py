class Client:
  """
  Handles all actions that a client machine can perform.
  
  Public threading:
    must be acquired before mutation, invocation, and dependent accesses
  """
  
  def __init__(self, realm, control):
    self.realm = realm
    self.control = control
    self.instance = None
    self.notify = None
    self.avatar = None
  
  def fileno(self):
    return self.control.fileno()
  
  def identity(self):
    """ Unique string identifying the client, composed of socket id and IP. """
    return "{0}".format(id(self))
  
  def debug(self, msg):
    """ Sends client-relevant debugging info to the server. """
    self.realm.debug("{0}: {1}".format(self.identity(), msg))
