from tkinter import *

from wclient.worldclient import WorldClient

class ClientUI:

  
  def __init__(self, client):
    self.rclient = client
    self.rclient.nhook = self.nhandle
    self.wclient = None
    
    self.avatar = None
    self.unit = None
    
    self.root = Tk()
    self.root.protocol("WM_DELETE_WINDOW", self.doquit)
    self.tdebug = Text(self.root, width=70, height=1, state=DISABLED)
    self.tdebug.grid(row=0)
    
    self.showselectavatar()

  
  def debug(self, item):
    self.tdebug.config(state=NORMAL)
    self.tdebug.delete(1.0, END)
    self.tdebug.insert(END, str(item))
    self.tdebug.config(state=DISABLED)

  
  def nhandle(self, n):
    if n.istype('RecvMessage'):
      s = "[{0}]: {1}\n".format(n.avatar, n.message)
      tar = self.chats
    else:
      s = str(n)
      tar = self.notifs
    
    if tar:
      tar.config(state=NORMAL)
      tar.insert(END, s)
      tar.config(state=DISABLED)
    else:
      print(s)

  
  def showselectavatar(self):
    self.selectavatar = Frame(self.root)
    self.avatar = Entry(self.selectavatar)
    self.avatar.bind("<Return>", self.doselectavatar)
    self.avatar.focus_set()
    
    self.selectavatar.grid(row=1)
    Label(self.selectavatar, text="Avatar").grid(row=0, column=0)
    self.avatar.grid(row=0, column=1)

  
  def doselectavatar(self, event):
    avatar = self.avatar.get()
    
    def handle(res):
      if res.istype('Success'):
        self.avatar = avatar
        self.selectavatar.destroy()
        self.showavatarui()
        self._startworld()
      else:
        self.debug("AvatarSelect failed.")
    self.rclient.selectavatar(avatar, handle)
  
  
  def _startworld(self):
    def handle(res):
      if res.istype('WorldInfo'):
        self.wclient = WorldClient()
        self.wclient.nhook = self.nhandle
        self.wclient.start(res.addr, res.cport, res.nport)
        self._selectunit(res.unitid, res.unitkey)
      else:
        raise Exception("Unexpected {0} (expecting WorldInfo)".format(res.type))
    self.rclient.getworldinfo(handle)
  
  
  def _selectunit(self, id, key):
    def handle(res):
      if res.istype('Success'):
        self.unit = id
        self.showworld()
      else:
        raise Exception("Failed to select unit: {0}".format(res.type))
    self.wclient.selectunit(id, key, handle)


  def showavatarui(self):
    self.avatarui = Frame(self.root)
    self.avatarui.grid(row=1)
    self.showchat()
  
  
  def showworld(self):
    self.world = Toplevel()
    self.world.protocol("WM_DELETE_WINDOW", self.doquitavatar)
  

  def showchat(self):
    self.chat = Frame(self.avatarui)
    self.notifs = Text(self.chat, width=70, height=2, state=DISABLED)
    self.chats = Text(self.chat, width=70, height=8, state=DISABLED)
    self.mrecip = Entry(self.chat, width=8)
    self.message = Entry(self.chat, width=45)
    self.message.bind("<Return>", self.dochat)
    
    self.chat.grid()
    self.notifs.grid(row=0, columnspan=4)
    self.chats.grid(row=1, columnspan=4)
    Label(self.chat, text="To").grid(row=2, column=0)
    self.mrecip.grid(row=2, column=1)
    Label(self.chat, text="say").grid(row=2, column=2)
    self.message.grid(row=2, column=3)

  
  def dochat(self, event):
    avatar = self.mrecip.get()
    message = self.message.get()
    self.message.delete(0, END)
    def handle(res):
      if res.istype('Success'):
        self.chats.config(state=NORMAL)
        self.chats.insert(END, "To [{0}]: {1}\n".format(avatar, message))
        self.chats.config(state=DISABLED)
      else:
        self.debug("SendMessage failed.")
    self.rclient.sendmessage(avatar, message, handle)

  
  def doquitavatar(self):
    def handle(res):
      if res.istype('Success'):
        self.unit = None
        self._quitworld()
      else:
        raise Exception("QuitUnit failed: {0}".format(res))
    self.wclient.quitunit(handle)
  
  
  def _quitworld(self):
    def handle(res):
      if res.istype('Success'):
        self.world.destroy()
        self.world = None
        self.wclient.destroy()
        self.wclient = None
        self._quitavatar()
      else:
        raise Exception("Failed to Quit world: {0}".format(res))
    self.wclient.quit(handle)
  
  
  def _quitavatar(self):
    def handle(res):
      if res.istype('Success'):
        self.avatar = None
        self.avatarui.destroy()
        self.avatarui = None
        self.showselectavatar()
      else:
        raise Exception("QuitAvatar failed: {0}".format(res))
    self.rclient.quitavatar(handle)
    
  
  def doquit(self):
    def handle(res):
      if res.istype('Success'):
        self.root.quit()
        self.rclient.destroy()
        self.rclient = None
      else:
        self.debug("Quit failed: {0}".format(res))
    self.rclient.quit(handle)


  def start(self):
    self.update()
    self.root.mainloop()
    
  
  def update(self):
    self.rclient.update()
    if self.wclient:
      self.wclient.update()
    self.root.after(1, self.update) #todo: try this at 0?
