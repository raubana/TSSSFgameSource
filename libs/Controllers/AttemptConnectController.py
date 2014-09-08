from Controller import*
import GameStartingController

from ..GUI.GUI import *
from ..netcom import Client

import string, os, thread

class AttemptConnectController(Controller):
	def init(self):
		#Clear the gui
		self.main.updated_elements = []
		self.main.main_element.clear()
		self.main.main_element.set_text("Connecting...")
		self.main.connecting = True

		self.client = Client(self.main.connect_data[0],self.main.connect_data[1])
		self.connect_time = 0
		self.prev_connected = False

		thread.start_new_thread(self.client.connect, tuple([]))

	def update(self):
		if self.client.connected:
			if not self.prev_connected:
				self.prev_connected = True
				self.connect_time = float(self.main.time)
				self.main.main_element.set_text("Connected. Sending client data...")
				self.client.send("CONNECT:"+self.main.connect_data[2])
			else:
				#we look for the permission to join the server
				if len(self.client.received_messages) > 0:
					message = self.client.received_messages.pop(0)
					if message.startswith("CONNECTED:"):
						self.main.connecting = False
						self.main.name = message[len("CONNECTED:"):]
						self.main.client = self.client
						self.main.controller = GameStartingController.GameStartingController(self.main)
				elif self.main.time-self.connect_time > TIMEOUT_TIME:
					self.client.close()
					import ConnectMenuController
					self.main.sound_lost_connection.play()
					self.main.controller = ConnectMenuController.ConnectMenuController(self.main)
					self.main.controller.message_element.set_text("Server Ignored Request")
		else:
			p = self.main.time%1.0
			count = p*4
			message = "Connecting"
			message += "."*int(count)
			self.main.main_element.set_text(message)
			if self.client.connection_status:
				self.client.close()
				import ConnectMenuController
				self.main.sound_lost_connection.play()
				self.main.controller = ConnectMenuController.ConnectMenuController(self.main)
				self.main.controller.message_element.set_text(self.client.connection_status)