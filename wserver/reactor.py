from wproto.message import Message

class Reactor:
  def __init__(self, mapping={}):
    self.mapping = mapping.copy()
  
  def register(self, action, reaction):
    self.mapping[action] = reaction
  
  def dispatch(self, client, action):
    reaction = self.mapping.get(action.type)
    if reaction:
      return reaction(client, action)
    else:
      raise Exception("No reactor registered for {0}".format(action.__class__))


class Reaction:
  """ An event that handles a client action. """
  READONLY = False
  
  def __init__(self, client, action):
    self.client = client
    self.action = action
    self.disconnect = False
    
  def process(self):
    res = self.react()
    if res == True:
      res = Message("Success")
    
    if res:
      self.client.debug("{0} => {1}".format(self.action, res))
      self.client.control.send(res)
    else:
      self.client.debug("{0} => (no response generated)".format(self.action))
    
    if self.disconnect:
      self.client.realm.removeclient(self.client)
    else:
      self.client.realm.idleclient(self.client)
  
  def react(self):
    raise Exception("Must extend Reaction.react in subclasses.")
