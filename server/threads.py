from threading import RLock

class Lockable:
  """
  This method provides a thread-safe lock to subclass instances AS LONG AS THEY
  REMEMBER TO CALL THE PARENT CONSTRUCTOR! It is intended to be used in a with
  statement as such:
  
    with some_lockable:
      some_lockable.some_unsafe_method()
  """
  
  def __init__(self):
    super().__init__()
    self.__lock = RLock()
  
  def __enter__(self):
    self.__lock.acquire()
    return self
  
  def __exit__(self, type_, value, traceback):
    self.__lock.release()
