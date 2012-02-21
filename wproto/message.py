class Message:
  
  def __init__(self, type, data={}, **kwargs):
    self.type = type
    self._data = data.copy()
    self._data.update(kwargs)
  
  def istype(self, type):
    return self.type == type
  
  def get(self, field):
    return self._data[field] if field in self._data else None
  
  def set(self, field, value):
    self._data[field] = value
  
  def __getattr__(self, field):
    return self.get(field)
  
  def __str__(self):
    return self.type+" "+str(self._data)
