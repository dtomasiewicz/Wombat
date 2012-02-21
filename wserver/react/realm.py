from wserver.reactor import Reaction
from wproto.message import Message

class RSelectAvatar(Reaction):
  def react(self):
    if self.client.avatar:
      return Message('InvalidAction')
    else:
      a = self.client.realm.avatar(self.action.avatar)
      if not a:
        return Message('InvalidAvatar', avatar=self.action.avatar)
      elif a.client:
        return Message('AvatarInUse')
      else:
        self.client.avatar = a
        a.client = self.client
        return True


class RQuitAvatar(Reaction):
  def react(self):
    if self.client.avatar:
      self.client.avatar.client = None
      self.client.avatar = None
      return True
    else:
      return Message('InvalidAction')


class RGetWorldInfo(Reaction):
  READONLY = True
  def react(self):
    if self.client.avatar:
      worldid, unitid, unitkey = self.client.avatar.worldinfo()
      addr, cport, nport = self.client.realm.worldlookup(worldid)
      return Message('WorldInfo', addr=addr, cport=cport, nport=nport,
                    worldid=worldid, unitid=unitid, unitkey=unitkey)
    else:
      return Message('InvalidAction')


class RSendMessage(Reaction):
  READONLY = True
  def react(self):
    if self.client.avatar:
      tar = self.client.realm.avatar(self.action.avatar)
      if not tar or not tar.client or not tar.client.notify:
        return Message('InvalidAvatar', avatar=self.action.avatar)
      else:
        tar.client.notify.send(Message('RecvMessage', avatar=self.client.avatar.name,
                                       message=self.action.message))
        return True
    else:
      return Message('InvalidAction')


REALM_REACTION = {
  'SelectAvatar': RSelectAvatar,
  'QuitAvatar': RQuitAvatar,
  'GetWorldInfo': RGetWorldInfo,
  'SendMessage': RSendMessage
}
