from Controller import*

from ..gui.GUI import *
from ..netcom import Client

import string, os, thread

class PreGameRoomController(Controller):
	def init(self):
		#Clear the gui
		self.main.updated_elements = []
		self.main.main_element.clear()
		self.main.main_element.set_text("In lobby.")

	def update(self):
		if len(self.main.client.received_messages) > 0:
			message = self.main.client.received_messages.pop(0)
			if message == PING_MESSAGE:
				self.main.client.send(PONG_MESSAGE)