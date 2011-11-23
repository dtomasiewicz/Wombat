from combatshared.control.response import *
from combatshared.notify.notification import *

from combatserver.reactor import Reaction, REALM, INSTANCE


class RQuit(Reaction):
  DOMAIN = REALM
  READONLY = False
  def react(self):
    if self.client.avatar:
      return InvalidAction()
    else:
      self.client.control.send(Success())
      return False

    
class RClaimNotify(Reaction):
  DOMAIN = REALM
  READONLY = False
  def react(self):
    self.client.notify = self.client.realm.claimnotify(self.action.key)
    return Success() if self.client.notify else InvalidNotifyKey()


class RAvatarSelect(Reaction):
  DOMAIN = REALM
  READONLY = False
  def react(self):
    if self.client.avatar:
      return InvalidAction()
    else:
      a = self.client.realm.avatar(self.action.avatar)
      if not a:
        return AvatarNoExists(self.action.avatar)
      elif a.client:
        return AvatarInUse()
      else:
        self.client.avatar = a
        a.client = self.client
        return Success()


class RAvatarQuit(Reaction):
  DOMAIN = REALM
  READONLY = False
  def react(self):
    if self.client.avatar:
      self.client.avatar.client = None
      self.client.avatar = None
      return Success()
    else:
      return InvalidAction()


class RSendMessage(Reaction):
  DOMAIN = REALM
  READONLY = True
  def react(self):
    if self.client.avatar:
      tar = self.client.realm.avatar(self.action.avatar)
      if not tar or not tar.client or not tar.client.notify:
        return AvatarNoExists(self.action.avatar)
      else:
        tar.client.notify.send(
            RecvMessage(self.client.avatar.name, self.action.message))
        return Success()
    else:
      return InvalidAction()