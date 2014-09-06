__author__ = 'dylan_000'

class Controller(object):
	def __init__(self, main):
		self.main = main
		self.init()

	def init(self):
		pass

	def handle_event_mousehover(self, widget, mouse_pos_local):
		pass

	def handle_event_mousepress(self, widget, mouse_pos_local, button):
		pass

	def handle_event_getfocus(self, widget):
		pass

	def handle_event_losefocus(self, widget):
		pass

	def handle_event_valuechange(self, widget):
		pass

	def handle_event_submit(self, widget):
		pass

	def read_message(self, message):
		pass

	def update(self):
		pass

	def move(self):
		pass

	def render(self):
		pass