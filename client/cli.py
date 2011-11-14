from cmd import Cmd
from argparse import ArgumentParser
from client import CombatClient

class ClientShell(Cmd):
  prompt = ">>> "
  
  def __init__(self, client):
    super().__init__()
    self.client = client
  
  def do_login(self, line):
    parser = ArgumentParser(description="Login to the combat server.")
    parser.add_argument('user')
    parser.add_argument('password')
    try:
      args = parser.parse_args(line.split())
      self.client.login(args.user, args.password)
    except SystemExit:
      pass
  
  def do_EOF(self, line):
    print("")
    if self.client.quit():
      return True
  
  def do_charselect(self, line):
    parser = ArgumentParser(description="Choose your character!")
    parser.add_argument('character')
    try:
      args = parser.parse_args(line.split())
      self.client.charselect(args.character)
    except SystemExit:
      pass
  
  def do_charquit(self, line):
    self.client.charquit()
  
  def do_logout(self, line):
    self.client.logout()
  
  def do_quit(self, line):
    if self.client.quit():
      return True
  
  def precmd(self, line):
    if len(self.client.debugs):
      print("=== NEW NOTIFICATIONS SINCE PREVIOUS COMMAND ===")
      self.dumpdebug(" ")
      print("================================================")
    
    return line
  
  def postcmd(self, stop, line):
    self.dumpdebug()
    return stop
    
  def dumpdebug(self, prefix = ""):
    while len(self.client.debugs):
      print(prefix+self.client.debugs.pop(0))
  
  
  def emptyline(self):
    pass
