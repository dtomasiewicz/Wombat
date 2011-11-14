from ..message import Message

# generic control action (sends a UTF-8 string)
class Response(Message):
  SUCCESS = False
    
class Success(Response):
  SUCCESS = True

class InvalidAction(Response):
  pass

class InvalidNotifyKey(Response):
  pass
