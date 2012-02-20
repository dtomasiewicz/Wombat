from cmd import Cmd
from argparse import ArgumentParser
from shlex import split

from wclient.worldclient import WorldClient


class ClientShell(Cmd):
  prompt = ">>> "
  
  def __init__(self, rclient):
    super().__init__()
    self.rclient = rclient
    self.wclient = None
  
  def do_EOF(self, line):
    print("")
    if self.rclient.quit().istype('Success'):
      return True
  
  def precmd(self, line):
    if len(self.rclient.debugs) or (self.wclient and len(self.wclient.debugs)):
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
    while len(self.rclient.debugs):
      print(self.rclient.debugs.pop(0))
    if self.wclient:
      while len(self.wclient.debugs):
        print(self.wclient.debugs.pop(0))
  
  def do_selectavatar(self, line):
    parser = ArgumentParser(description="Choose your avatar!")
    parser.add_argument('avatar')
    try:
      args = parser.parse_args(split(line))
      if self.rclient.selectavatar(args.avatar).istype('Success'):
        wi = self.rclient.getworldinfo()
        if wi.istype('Success'):
          self.wclient = WorldClient()
          self.wclient.start(wi.addr, wi.cport, wi.nport)
          self.wclient.selectunit(wi.unitid, wi.unitkey)
    except SystemExit:
      pass
  
  do_sa = do_selectavatar
  
  def do_quitavatar(self, line):
    self.rclient.quitavatar()
  
  do_qa = do_quitavatar
  
  def do_quit(self, line):
    if not self.wclient or self.wclient.quit().istype('Success'):
      if self.rclient.quit().istype('Success'):
        return True
    return False
  
  do_exit = do_q = do_quit
  
  def do_msg(self, line):
    parser = ArgumentParser(description="Send a message to another avatar.")
    parser.add_argument('avatar')
    parser.add_argument('message')
    try:
      args = parser.parse_args(split(line))
      self.rclient.sendmessage(args.avatar, args.message)
    except SystemExit:
      pass
      
  do_m = do_msg
  
