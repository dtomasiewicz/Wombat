from ..message import Message

# generic control action (sends a UTF-8 string)
class Action(Message):
  pass

class GetIdentity(Action):
  pass

# Type(bytelen)  Data
# short          client ID
class Identify(Action):
  SIMPLE = False
  
  def __init__(self, clientid):
    self.clientid = clientid
  
  def pack(self):
    return ('H', self.clientid)
  
  def unpack(stream):
    return Identify(stream.recvshort())

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
    usrb = bytes(self.user, self.STR_ENC)
    ul = len(usrb)
    pwdb = bytes(self.password, self.STR_ENC)
    pl = len(pwdb)
    return ('H{0}sH{1}s'.format(ul, pl), ul, usrb, pl, pwdb)
    
  def unpack(stream):
    usr = stream.recvstring(stream.recvshort(), __class__.STR_ENC)
    pwd = stream.recvstring(stream.recvshort(), __class__.STR_ENC)
    return Login(usr, pwd)

class Logout(Action):
  pass

class Quit(Action):
  pass


# Type(bytelen)  Data
# short          character name byte-length (l)
# string(l)      character name
class CharSelect(Action):
  SIMPLE = False
  
  def __init__(self, char):
    self.char = char
    
  def pack(self):
    cb = bytes(self.char, self.STR_ENC)
    cl = len(cb)
    return ('H{0}s'.format(cl), cl, cb)
  
  def unpack(stream):
    return CharSelect(stream.recvstring(stream.recvshort(), __class__.STR_ENC))

class CharQuit(Action):
  pass
