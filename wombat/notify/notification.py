from wombat.message import Message

class Notification(Message):
  pass

class NotifyKey(Notification):
  SIMPLE = False
  
  def __init__(self, key):
    self.key = key
  
  def pack(self):
    return ('H', self.key)
  
  def unpack(stream):
    return NotifyKey(stream.recvshort())

# Type(bytelen)  Data
# short          sender's name byte-length (c)
# string(c)      sender's name
# short          message byte-length (m)
# string(m)      message
class RecvMessage(Notification):
  SIMPLE = False
  
  def __init__(self, char, message):
    self.char = char
    self.message = message

  def pack(self):
    cb = bytes(self.char, self.STR_ENC)
    cl = len(cb)
    mb = bytes(self.message, self.STR_ENC)
    ml = len(mb)
    return ('H{0}sH{1}s'.format(cl, ml), cl, cb, ml, mb)
  
  def unpack(stream):
    char = stream.recvstring(stream.recvshort(), __class__.STR_ENC)
    message = stream.recvstring(stream.recvshort(), __class__.STR_ENC)
    return RecvMessage(char, message)
