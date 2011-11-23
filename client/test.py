#!/usr/bin/env python
from time import sleep

from client import CombatClient

c = CombatClient()
c.start('127.0.0.1', 10000, 10001)
c.avatarselect("Test")
sleep(1)
c.sendmessage("Test", "hello")
c.sendmessage("nonexistent", "hello")
if not c.quit().SUCCESS:
  c.avatarquit()
  c.quit()

for s in c.debugs:
  print(s)
