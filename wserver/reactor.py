from wshared.control.response import Response


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

