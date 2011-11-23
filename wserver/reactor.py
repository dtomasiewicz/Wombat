from wshared.control.response import Response


REALM = "Realm"
INSTANCE = "Instance"


class Reactor:
  def __init__(self, mapping={}):
    self.mapping = mapping
  
  def register(self, actioncls, reactcls):
    self.mapping[actioncls] = reactcls
  
  def dispatch(self, client, action):
    reactcls = self.mapping.get(action.__class__)
    if reactcls:
      return reactcls(client, action)
    else:
      raise Exception("No reactor registered for {0}".format(action.__class__))


class Reaction:
  """ An event that handles a client action. """
  DOMAIN = None
  READONLY = None
  
  def __init__(self, client, action):
    self.client = client
    self.action = action
    
  def process(self):
    res = self.react()
    if res:
      self.client.debug("{0} => {1}".format(self.action, res))
      self.client.control.send(res)
      self.client.realm.idleclient(self.client)
    else:
      self.client.realm.removeclient(self.client)
  
  def react(self):
    raise Exception("Must extend Reaction.process in subclasses.")
