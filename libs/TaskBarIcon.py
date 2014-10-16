import pygame

import wx, thread


class TaskBarIcon(wx.TaskBarIcon):
	def __init__(self):
		self.app = wx.PySimpleApp()
		super(TaskBarIcon, self).__init__()
		self.set_icon("imgs/tiny_window_icon.png")
		self.Bind(wx.EVT_TASKBAR_LEFT_DOWN, self.on_left_down)
		self.run_thread()

	def run_thread(self):
		thread.start_new_thread(self._run, tuple([]))

	def _run(self):
		self.app.MainLoop()

	def create_menu_item(self, menu, label, func):
		item = wx.MenuItem(menu, -1, label)
		menu.Bind(wx.EVT_MENU, func, id=item.GetId())
		menu.AppendItem(item)
		return item

	def CreatePopupMenu(self):
		menu = wx.Menu()
		return menu

	def set_icon(self, path):
		icon = wx.IconFromBitmap(wx.Bitmap(path))
		self.SetIcon(icon, "TSSSFgame")

	def on_left_down(self, event):
		pass
		#TODO: Make the window get focus.

	def on_exit(self, event):
		wx.CallAfter(self.Destroy)