from cmd import Cmd
from argparse import ArgumentParser
from shlex import split

class ClientShell(Cmd):
  prompt = ">>> "
  
  def __init__(self, client):
    super().__init__()
    self.client = client
  
  def do_EOF(self, line):
    print("")
    if self.client.quit().SUCCESS:
      return True
  
  def precmd(self, line):
    if len(self.client.debugs):
      print("=== NEW NOTIFICATIONS SINCE PREVIOUS COMMAND ===")
      self.dumpdebug()
      print("================================================")
    return line
  
  def postcmd(self, stop, line):
    self.dumpdebug()
    return stop
  
  def emptyline(self):
    pass
    
  def dumpdebug(self):
    while len(self.client.debugs):
      print(self.client.debugs.pop(0))
  
  def do_login(self, line):
    parser = ArgumentParser(description="Login to the combat server.")
    parser.add_argument('user')
    parser.add_argument('password')
    try:
      args = parser.parse_args(split(line))
      self.client.login(args.user, args.password)
    except SystemExit:
      pass
  
  def do_li(self, line):
    return self.do_login(line)
  
  def do_avatarselect(self, line):
    parser = ArgumentParser(description="Choose your avatar!")
    parser.add_argument('avatar')
    try:
      args = parser.parse_args(split(line))
      self.client.avatarselect(args.avatar)
    except SystemExit:
      pass
  
  def do_as(self, line):
    return self.do_avatarselect(line)
  
  def do_avatarquit(self, line):
    self.client.avatarquit()
  
  def do_aq(self, line):
    return self.do_avatarquit(line)
  
  def do_logout(self, line):
    self.client.logout()
  
  def do_lo(self, line):
    return self.do_logout(line)
  
  def do_quit(self, line):
    if self.client.quit().SUCCESS:
      return True
  
  def do_q(self, line):
    return self.do_quit(line)
  
  def do_exit(self, line):
    return self.do_quit(line)

  def do_msg(self, line):
    parser = ArgumentParser(description="Send a message to another avatar.")
    parser.add_argument('avatar')
    parser.add_argument('message')
    try:
      args = parser.parse_args(split(line))
      self.client.sendmessage(args.avatar, args.message)
    except SystemExit:
      pass
  
  def do_m(self, line):
    return self.do_msg(line)
