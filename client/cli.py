from cmd import Cmd
from argparse import ArgumentParser
from client import CombatClient

class ClientShell(Cmd):
  prompt = "Command >>> "
  
  def __init__(self):
    super().__init__()
    self.client = CombatClient()
    
  def do_start(self, line):
    parser = ArgumentParser(description="Connect to the combat server.")
    parser.add_argument('-r', default='127.0.0.1')
    parser.add_argument('-c', type=int, default=10000)
    parser.add_argument('-n', type=int, default=10001)
    args = parser.parse_args(line.split())
    self.client.start(args.r, args.c, args.n)
  
  def do_login(self, line):
    parser = ArgumentParser(description="Login to the combat server.")
    parser.add_argument('user')
    parser.add_argument('password')
    args = parser.parse_args(line.split())
    self.client.login(args.user, args.password)
  
  def do_EOF(self, line):
    print("")
    return True
  
  def do_charselect(self, line):
    parser = ArgumentParser(description="Choose your character!")
    parser.add_argument('character')
    args = parser.parse_args(line.split())
    self.client.charselect(args.character)
  
  def do_charquit(self, line):
    self.client.charquit()
  
  def do_logout(self, line):
    self.client.logout()
  
  def do_quit(self, line):
    self.client.quit()
  
  def precmd(self, line):
    if len(self.client.debug):
      print("=== NEW NOTIFICATIONS SINCE PREVIOUS COMMAND ===")
      self.dumpdebug(" ")
      print("================================================")
    return line
  
  def postcmd(self, stop, line):
    self.dumpdebug()
    return stop
    
  def dumpdebug(self, prefix = ""):
    while len(self.client.debug):
      print(prefix+self.client.debug.pop(0))
  
  
  def emptyline(self):
    pass
