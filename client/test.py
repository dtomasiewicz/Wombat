#!/usr/bin/env python
from client import CombatClient

c = CombatClient()
c.start('127.0.0.1', 10000, 10001)
c.login('Daniel', 'Test')
c.charselect("Blastoise")
c.charquit()
c.logout()
c.login('John', 'Hancock')
c.quit()
c.logout()
c.quit()