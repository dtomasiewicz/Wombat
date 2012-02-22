class Model:
  """ Base model for persistent relational data storage. """
  
  TABLE = 'model'
  SCHEMA = {
    'id' : {'type': int}
  }
  PRIMARY_KEY = 'id'
  
  def __init__(self, source, attrs=None):
    self._source = source
    self._attrs = {}
    for field,cfg in self.SCHEMA.items():
      default = cfg['default'] if 'default' in cfg else None
      # cast to correct python type
      self._attrs[field] = cfg['type'](attrs.get(field)) if attrs else default
    self._dirty = False if attrs else True
    self._init()
  
    
  def get(self, name):
    if name in self._attrs:
      return self._attrs[name]
    else:
      raise Exception("Getting non-existent field: {0}".format(name))
  
  
  def set(self, name, value):
    if name in self.SCHEMA:
      # cast to correct python type
      self._attrs[name] = self.SCHEMA[name]['type'](value)
      self._dirty = True
    else:
      raise Exception("Setting non-existent field: {0}".format(name))
  
  
  def __getattr__(self, name):
    return self.get(name)


  def write(self):
    """ Writes the model's attributes to the database. """
    if self._attrs[self.PRIMARY_KEY] == None:
      # new record
      fields = []
      params = []
      values = []
      for field,value in self._attrs.items():
        if field != self.PRIMARY_KEY:
          fields.append(field)
          params.append(value)
          values.append('${0}'.format(len(params)))
      sql = "INSERT INTO {table} ({fields}) VALUES ({values}) RETURNING {pkey}".format(
          table=self.TABLE, fields=", ".join(fields), values=", ".join(values), pkey=self.PRIMARY_KEY)
      print(sql)
      ident = self._source.prepare(sql).first(*params)
      self._attrs[self.PRIMARY_KEY] = ident
    else:
      # existing record
      values = ", ".join((a+'=$'+str(i+1) for i,a in enumerate(self._attrs.keys())))
      assigns = []
      params = []
      for field,value in self._attrs.items():
        if field != self.PRIMARY_KEY:
          params.append(value)
          assigns.append('{0}=${1}'.format(field, len(params)))
      params.append(self._attrs[self.PRIMARY_KEY])
      sql = "UPDATE {table} SET {assigns} WHERE {pkey}=${pkparam}".format(
          table=self.TABLE, assigns=", ".join(assigns), pkey=self.PRIMARY_KEY,
          pkparam=len(params))
      print(sql)
      params = self._attrs.values()
      self._source.prepare(sql).first(*params)
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

  @classmethod
  def _parsewhere(cls, where, params, kwconds):
    conds = []
    if where:
      conds = [where]
    if len(kwconds):
      conds += (a+'=$'+str(i+len(params)+1) for i,a in enumerate(kwconds.keys()))
      params += tuple(kwconds.values())
    sql = " WHERE " + " AND ".join(conds) if len(conds) else ""
    return (sql,) + tuple(params)

  @classmethod
  def _modelgen(cls, source, results):
    for row in results:
      yield cls(source, row)
