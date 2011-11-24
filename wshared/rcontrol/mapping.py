from wshared.rcontrol.action import *
from wshared.rcontrol.response import *


ACTION_MAPPING = {
  100: AvatarSelect,
  101: AvatarQuit,
  102: SendMessage
}

RESPONSE_MAPPING = {
  100: AvatarNoExists,
  101: AvatarInUse
}
