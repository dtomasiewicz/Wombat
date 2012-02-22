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
    self.avatar = None
    self.unit = None
    
    
  def dumpdebug(self):
    while len(self.rclient.debugs):
      print("RLM: "+self.rclient.debugs.pop(0))
    if self.wclient:
      while len(self.wclient.debugs):
        print("WLD: "+self.wclient.debugs.pop(0))
    
  
  def do_EOF(self, line):
    print("")
    self.rclient.quit()
    return True
  
  
  def precmd(self, line):
    self.rclient.update()
    if self.wclient:
      self.wclient.update()
    if len(self.rclient.debugs) or (self.wclient and len(self.wclient.debugs)):
      print("=== NEW NOTIFICATIONS SINCE PREVIOUS COMMAND ===")
      self.dumpdebug()
      print("================ COMMAND OUTPUT ================")
    return line
  
  
  def postcmd(self, stop, line):
    if stop:
      if self.wclient:
        self.wclient.destroy()
        self.wclient = None
      self.rclient.destroy()
      self.rclient = None
    return stop
  
  
  def emptyline(self):
    pass
  
  
  def do_selectavatar(self, line):
    parser = ArgumentParser(description="Choose your avatar!")
    parser.add_argument('avatar')
    try:
      args = parser.parse_args(split(line))
      res = self.rclient.selectavatar(args.avatar)
      if res.istype('Success'):
        self._startworld()
      else:
        print("AvatarSelect failed: {0}".format(res))
    except SystemExit:
      pass
  
  do_sa = do_selectavatar
  
  
  def _startworld(self):
    res = self.rclient.getworldinfo()
    if res.istype('WorldInfo'):
      self.wclient = WorldClient()
      self.wclient.start(res.addr, res.cport, res.nport, True)
      self._selectunit(res.unitid, res.unitkey)
    else:
      raise Exception("Unexpected {0} (expecting WorldInfo)".format(res))
    
  
  
  def _selectunit(self, id, key):
    res = self.wclient.selectunit(id, key)
    if res.istype('Success'):
      self.unit = id
    else:
      raise Exception("Failed to select unit: {0}".format(res))
    
  
  def do_quitavatar(self, line):
    res = self.wclient.quitunit()
    if res.istype('Success'):
      self.unit = None
      self._quitworld()
    else:
      raise Exception("QuitUnit failed: {0}".format(res))
  
  do_qa = do_quitavatar
  
  
  def _quitworld(self):
    res = self.wclient.quit()
    if res.istype('Success'):
      self.wclient.destroy()
      self.wclient = None
      self._quitavatar()
    else:
      raise Exception("Failed to Quit world: {0}".format(res))
  
  
  def _quitavatar(self):
    res = self.rclient.quitavatar()
    if res.istype('Success'):
      self.avatar = None
    else:
      raise Exception("QuitAvatar failed: {0}".format(res))
    
  
  def do_quit(self, line):
    res = self.rclient.quit()
    if res.istype('Success'):
      self.rclient.destroy()
      self.rclient = None
      return True
    else:
      print("Quit failed: {0}".format(res))
      return False
  
  do_exit = do_q = do_quit
  
  
  def do_msg(self, line):
    parser = ArgumentParser(description="Send a message to another avatar.")
    parser.add_argument('avatar')
    parser.add_argument('message')
    try:
      args = parser.parse_args(split(line))
      res = self.rclient.sendmessage(args.avatar, args.message)
      if not res.istype('Success'):
        print("SendMessage failed: {0}".format(res))
    except SystemExit:
      pass
      
  do_m = do_msg
  
