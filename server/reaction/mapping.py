from combatshared.control.action import *
from combatserver.reaction import realm

REACTION_MAPPING = {
  Quit: realm.RQuit,
  ClaimNotify: realm.RClaimNotify,
  AvatarSelect: realm.RAvatarSelect,
  AvatarQuit: realm.RAvatarQuit,
  SendMessage: realm.RSendMessage
}