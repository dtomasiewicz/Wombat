from wproto.message import Message
from wproto.packutils import prepack, recvstring

class Response(Message):
  SUCCESS = False
    
class Success(Response):
  SUCCESS = True

class InvalidAction(Response):
  pass

class InvalidNotifyKey(Response):
  pass
