from wshared.control.action import *
from wshared.control.response import *

ACTION_MAPPING = {
  1: Quit,
  2: ClaimNotify,
  3: AvatarSelect,
  4: AvatarQuit,
  5: SendMessage
}

RESPONSE_MAPPING = {
  1: Success,
  2: InvalidAction,
  3: InvalidNotifyKey,
  4: AvatarNoExists,
  5: AvatarInUse
}
