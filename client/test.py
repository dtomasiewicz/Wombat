#!/usr/bin/env python
from time import sleep

from client import CombatClient

c = CombatClient()
c.start('127.0.0.1', 10000, 10001)
c.login('Daniel', 'Test')
c.avatarselect("Blastoise")
#sleep(2)
c.avatarquit()
c.logout()
c.login('John', 'Hancock')
c.quit()
c.logout()
c.quit()

for s in c.debugs:
  print(s)