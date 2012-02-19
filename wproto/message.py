class Message:
  def __init__(self, alias, data={}, **kwargs):
    self.alias = alias
    self.data = data.copy()
    self.data.update(kwargs)
  
  def get(field):
    return self.data[field] if field in self.data else None
  
  def __str__(self):
    return self.alias
