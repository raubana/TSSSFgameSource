from Controller import*

from ..gui.GUI import *
from ..netcom import Client

import string, os, thread

class AttemptConnectController(Controller):
	def init(self):
		#Clear the gui
		self.main.updated_elements = []
		self.main.main_element.clear()
		self.main.main_element.set_text("Connecting...")

		self.client = Client(self.main.connect_data[0],self.main.connect_data[1])

		thread.start_new_thread(self.client.connect, tuple([]))

	def update(self):
		if self.client.connected:
			#TODO: Finish connecting
			self.main.main_element.set_text("Connected!")
		elif self.client.connection_status:
			import ConnectMenuController
			self.main.controller = ConnectMenuController.ConnectMenuController(self.main)
			self.main.controller.message_element.set_text(self.client.connection_status)
		else:
			p = self.main.time%1.0
			count = p*4
			message = "Connecting"
			message += "."*int(count)
			self.main.main_element.set_text(message)