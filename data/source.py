from postgresql.driver import connect

class Source:
  
  def __init__(self, config):
    self._db = connect(**config)

  def prepare(self, sql):
    return self._db.prepare(sql)
  
  def execute(self, sql):
    return self._db.execute(sql)
