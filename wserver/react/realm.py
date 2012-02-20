from wserver.reactor import Reaction
from wproto.message import Message

class RSelectAvatar(Reaction):
  READONLY = False
  def react(self):
    if self.client.avatar:
      return Message('InvalidAction')
    else:
      a = self.client.realm.avatar(self.action.get('avatar'))
      if not a:
        return Message('InvalidAvatar', avatar=self.action.get('avatar'))
      elif a.client:
        return Message('AvatarInUse')
      else:
        self.client.avatar = a
        a.client = self.client
        return Message('Success')


class RQuitAvatar(Reaction):
  READONLY = False
  def react(self):
    if self.client.avatar:
      self.client.avatar.client = None
      self.client.avatar = None
      return Message('Success')
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
      tar = self.client.realm.avatar(self.action.get('avatar'))
      if not tar or not tar.client or not tar.client.notify:
        return Message('InvalidAvatar', avatar=self.action.get('avatar'))
      else:
        tar.client.notify.send(Message('RecvMessage', avatar=self.client.avatar.name,
                                       message=self.action.get('message')))
        return Message('Success')
    else:
      return Message('InvalidAction')


REALM_REACTION = {
  'SelectAvatar': RSelectAvatar,
  'QuitAvatar': RQuitAvatar,
  'GetWorldInfo': RGetWorldInfo,
  'SendMessage': RSendMessage
}
