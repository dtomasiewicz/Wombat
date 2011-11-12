from .action import *
from .response import *

ACTION_MAPPING = {
  1: GetIdentity,
  2: Identify,
  3: Login,
  4: Logout,
  5: Quit,
  6: CharSelect,
  7: CharQuit
}

RESPONSE_MAPPING = {
  1: Success,
  2: InvalidAction,
  3: Identity,
  4: InvalidIdentity,
  5: RemapNotify
}
