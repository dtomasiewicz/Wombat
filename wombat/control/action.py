from wombat.message import Message
from wombat.packutils import prepack, recvstring, recvintus

# generic control action (sends a UTF-8 string)
class Action(Message):
  pass

# Type(bytelen)  Data
# short          notify key
class ClaimNotify(Action):
  SIMPLE = False
  
  def __init__(self, key):
    self.key = key
  
  def pack(self):
    return prepack(self.key)
  
  def unpack(sock):
    return ClaimNotify(recvintus(sock))

# Type(bytelen)  Data
# short          user name byte-length (u)
# string(u)      user name
# short          password byte-length (p)
# string(p)      password
class Login(Action):
  SIMPLE = False
  
  def __init__(self, usr, pwd):
    self.user = usr
    self.password = pwd
  
  def pack(self):
    return prepack(self.user, self.password)
    
  def unpack(sock):
    return Login(recvstring(sock), recvstring(sock))

class Logout(Action):
  pass

class Quit(Action):
  pass

# Type(bytelen)  Data
# short          avatar name byte-length (l)
# string(l)      avatar name
class AvatarSelect(Action):
  SIMPLE = False
  
  def __init__(self, avatar):
    self.avatar = avatar
    
  def pack(self):
    return prepack(self.avatar)
  
  def unpack(sock):
    return AvatarSelect(recvstring(sock))

class AvatarQuit(Action):
  pass

# Type(bytelen)  Data
# short          avatar name byte-length (a)
# string(a)      avatar name
# short          message byte-length (m)
# string(m)      message
class SendMessage(Action):
  SIMPLE = False
  
  def __init__(self, avatar, message):
    self.avatar = avatar
    self.message = message

  def pack(self):
    return prepack(self.avatar, self.message)
  
  def unpack(sock):
    return SendMessage(recvstring(sock), recvstring(sock))
