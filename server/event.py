class Event:
  def __init__(self, callback, *args, **kwargs):
    self.callback = callback
    self.args = args
    self.kwargs = kwargs
  
  def process(self):
    self.callback(*self.args, **self.kwargs)
