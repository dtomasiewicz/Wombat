from wshared.control.action import *
from wshared.control.response import *

ACTION_MAPPING = {
  0: Quit,
  1: ClaimNotify
}

RESPONSE_MAPPING = {
  0: Success,
  1: InvalidAction,
  2: InvalidNotifyKey
}
