from .action import *
from .response import *

ACTION_MAPPING = {
  1: ClaimNotify,
  2: Login,
  3: Logout,
  4: Quit,
  5: CharSelect,
  6: CharQuit,
  7: SendMessage
}

RESPONSE_MAPPING = {
  1: Success,
  2: InvalidAction,
  3: InvalidNotifyKey,
  4: CharNoExists
}
