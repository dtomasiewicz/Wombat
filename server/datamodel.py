from threading import RLock

class Model:
  
  def __init__(self, source, attrs):
    self._source = source
    self._lock = RLock()
    self._attrs = {}
    for index, field in enumerate(self.SCHEMA):
      self._attrs[field] = attrs[index]
    self._dirty = False
    self._init()
    
  def get(self, name):
    if name in self._attrs:
      return self._attrs[name]
    else:
      raise Exception("Getting non-existent field: {0}".format(name))
  
  def set(self, name, value):
    if name in self._attrs:
      self._attrs[name] = value
    else:
      raise Exception("Setting non-existent field: {0}".format(name))
  
  def __getattr__(self, name):
    return self.get(name)
  
  def __enter__(self):
    self._lock.acquire()
    return self
  
  def __exit__(self, type, value, traceback):
    if self._dirty:
      self.write()
    self._lock.release()

  def write(self):
    """ Writes the model's attributes to the database. """
    values = ", ".join((a+'=$'+str(i+1) for i,a in enumerate(self._attrs.keys())))
    sql = "UPDATE {table} SET {values} WHERE id = {id}".format(
        table=self.TABLE, values=values, id=self.get('id'))
    self._source.prepare(sql)(*self._attrs.values())
    self._dirty = False
  
  @classmethod
  def first(cls, source, where=None, *params, **kwconds):
    sql = "SELECT * FROM "+cls.TABLE
    where, *params = Model._parsewhere(where, params, kwconds)
    res = source.prepare(sql + where).first(*params)
    return cls(source, res) if res else None
    
  @classmethod
  def all(cls, source, where=None, *params, **kwconds):
    sql = "SELECT * FROM "+cls.TABLE
    where, *params = Model._parsewhere(where, params, kwconds)
    return Model._modelgen(cls, source, source.prepare(sql + where).rows(*params))
  
  def _parsewhere(where, params, kwconds):
    conds = []
    if where:
      conds = [where]
    if len(kwconds):
      conds += (a+'=$'+str(i+len(params)+1) for i,a in enumerate(kwconds.keys()))
      params += tuple(kwconds.values())
    sql = " WHERE " + " AND ".join(conds) if len(conds) else ""
    return (sql,) + tuple(params)
  
  def _modelgen(cls, source, results):
    for row in results:
      yield cls(source, row)
