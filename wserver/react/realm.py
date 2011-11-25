from wshared.control.realm import *
from wshared.control.game import Success
from wshared.notify.realm import *

from wserver.reactor import Reaction


class RSelectAvatar(Reaction):
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


class RQuitAvatar(Reaction):
  READONLY = False
  def react(self):
    if self.client.avatar:
      self.client.avatar.client = None
      self.client.avatar = None
      return Success()
    else:
      return InvalidAction()


class RGetInstance(Reaction):
  READONLY = True
  def react(self):
    if self.client.avatar:
      return InstanceInfo(*self.client.avatar.instanceinfo())
    else:
      return InvalidAction()


class RSendMessage(Reaction):
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


REALM_REACTION = {
  SelectAvatar: RSelectAvatar,
  QuitAvatar: RQuitAvatar,
  GetInstance: RGetInstance,
  SendMessage: RSendMessage
}
