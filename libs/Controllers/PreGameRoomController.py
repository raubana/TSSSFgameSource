from Controller import*

from ..GUI.GUI import *
from ..netcom import Client

import string, os, thread

class PreGameRoomController(Controller):
	def init(self):
		#Clear the gui
		self.main.updated_elements = []
		self.main.main_element.clear()
		self.main.main_element.set_text("")

		self.chat_window = Element(self.main, self.main.main_element, None, ("100%","90%"), bg_color=(255,255,255))

		self.text_inputbox = InputBox(self.main, self.main.main_element, None, ("100%",self.main.font.get_height()+4))
		self.text_inputbox.max_characters = 50

		self.text_inputbox.add_handler_submit(self)

	def update(self):
		if len(self.main.client.received_messages) > 0:
			message = self.main.client.received_messages.pop(0)
			if message == PING_MESSAGE:
				self.main.client.send(PONG_MESSAGE)
			elif message.startswith("ADD_CHAT:"):
				chat = message[len("ADD_CHAT:"):]
				element = Element(self.main, self.chat_window, None, ("100%",self.main.font.get_height()), bg_color=None)
				if len(self.chat_window.children) > 15:
					self.chat_window._remove_child(self.chat_window.children[0])

	def handle_event_submit(self, widget):
		message = self.text_inputbox.text

		self.main.client.send("CHAT:"+message)

		self.text_inputbox.set_text("")
		self.text_inputbox.index = 0
		self.text_inputbox.offset = 0