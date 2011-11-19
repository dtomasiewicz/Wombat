from tkinter import *

from wombat.notify.notification import *

class ClientUI:
  
  def __init__(self, client):
    self.client = client
    self.client.nhook = self.nhandle
    self.root = Tk()
    self.root.protocol("WM_DELETE_WINDOW", self.doquit)
    self.tdebug = Text(self.root, width=70, height=1, state=DISABLED)
    self.tdebug.grid(row=0)
    self.showlogin()
  
  def debug(self, item):
    self.tdebug.config(state=NORMAL)
    self.tdebug.delete(1.0, END)
    self.tdebug.insert(END, str(item))
    self.tdebug.config(state=DISABLED)
  
  def nhandle(self, n):
    if isinstance(n, RecvMessage):
      s = "[{0}]: {1}\n".format(n.avatar, n.message)
      tar = self.chats
    else:
      s = n.__str__()
      tar = self.notifs
    
    if tar:
      tar.config(state=NORMAL)
      tar.insert(END, s)
      tar.config(state=DISABLED)
    else:
      print(s)
    
  def showlogin(self):
    self.login = Frame(self.root)
    self.user = Entry(self.login)
    self.password = Entry(self.login, show='*')
    self.password.bind("<Return>", self.dologin)
    self.user.focus_set()
    
    self.login.grid(row=1)
    Label(self.login, text="User").grid(row=0, column=0)
    self.user.grid(row=0, column=1)
    Label(self.login, text="Password").grid(row=1, column=0)
    self.password.grid(row=1, column=1)
  
  def dologin(self, event):
    res = self.client.login(self.user.get(), self.password.get())
    if res.SUCCESS:
      self.login.destroy()
      self.showavatarselect()
    else:
      self.password.delete(0, END)
      self.password.focus_set()
      self.debug("Login failed.")
  
  def showavatarselect(self):
    self.avatarselect = Frame(self.root)
    self.avatar = Entry(self.avatarselect)
    self.avatar.bind("<Return>", self.doavatarselect)
    self.avatar.focus_set()
    
    self.avatarselect.grid(row=1)
    Label(self.avatarselect, text="Avatar").grid(row=0, column=0)
    self.avatar.grid(row=0, column=1)
  
  def doavatarselect(self, event):
    if self.client.avatarselect(self.avatar.get()).SUCCESS:
      self.avatarselect.destroy()
      self.showavatarui()
    else:
      self.debug("AvatarSelect failed.")
  
  def showavatarui(self):
    self.avatarui = Frame(self.root)
    self.avatarui.grid(row=1)
    self.showchat()
  
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
    if self.client.sendmessage(avatar, message).SUCCESS:
      self.message.delete(0, END)
      self.chats.config(state=NORMAL)
      self.chats.insert(END, "To [{0}]: {1}\n".format(avatar, message))
      self.chats.config(state=DISABLED)
    else:
      self.debug("SendMessage failed.")
  
  def doavatarquit(self):
    if self.client.avatarquit().SUCCESS:
      if self.avatarui:
        self.avatarui.destroy()
        self.avatarui = None
      return True
    else:
      self.debug("AvatarQuit failed.")
    return False
      
  def dologout(self):
    if not self.client.avatar or self.doavatarquit():
      if self.client.logout().SUCCESS:
        if self.login:
          self.login.destroy()
          self.login = None
        return True
      else:
        self.debug("Logout failed.")
    return False
  
  def doquit(self):
    if not self.client.user or self.dologout():
      if self.client.quit().SUCCESS:
        self.root.quit()
        return True
      else:
        self.debug("Quit failed.")
    return False

  def start(self):
    self.root.mainloop()
