from Controller import*

from ..GUI.GUI import *
from ..netcom import Client
from ..Deck import MasterDeck, Card
from ..PickledCard import *

import string, os, thread, io

class GameStartingController(Controller):
	def init(self):
		#Clear the gui
		self.main.updated_elements = []
		self.main.main_element.clear()

		self.number_of_cards = None
		self.main.master_deck = MasterDeck()

		self.current_message = "REQUESTING DECK SIZE"

		self.main.client.send("REQUEST_DECKSIZE")

	def update(self):
		#Ping
		if self.main.client.connected:
			lgm = self.main.client.server_last_got_message
			dif = self.main.time - lgm
			if dif >= PING_FREQUENCY:
				if not self.server_is_pinged:
					self.server_is_pinged = True
					self.main.client.send(PING_MESSAGE)
				else:
					# This means the server was already sent a 'ping', and we're waiting for a 'pong'
					if dif >= PING_FREQUENCY + TIMEOUT_TIME:
						#This server has timed out, so we must disconnect
						print "= Server has timed-out."
						self.main.client.close()
			else:
				self.server_is_pinged = False
		#Everything Else
		if self.main.client.connected:
			if len(self.main.client.received_messages) > 0:
				message = self.main.client.received_messages.pop(0)
				print message[:100]
				if message == PING_MESSAGE:
					self.main.client.send(PONG_MESSAGE)
				elif message.startswith("DECKSIZE:"):
					self.number_of_cards = int(message[len("DECKSIZE:")])
					if self.number_of_cards > 0:
						self.main.client.send("REQUEST_CARDFILE:0")
					else:
						print "EMPTY DECK!!"
						self.main.client.close()
				elif message == "CARDFILE:":
					s1 = message[len("CARDFILE:"):]
					s2 = message[:s1.index(":")]
					print "RECEIVED CARD "+s2+"/"+str(self.number_of_cards)
					self.current_message = s2+"/"+str(self.number_of_cards)
					index = int(s2)
					s3 = s1[len(s2)+1:]
					f = open_pickledcard(io.BytesIO(s3))
					self.main.master_deck.unpickle_and_add_card(f)
					if len(self.main.master_deck.cards) == self.number_of_cards:
						self.main.client.send("DONE_AND_WAITING")
					else:
						self.main.client.send("REQUEST_CARDFILE:"+str(len(self.main.master_deck.cards)))
				elif message == "GAME_START":
					self.current_message = "The game would have started here. Please close the program."
		elif self.main.client.connection_status:
			import ConnectMenuController
			self.main.sound_lost_connection.play()
			self.main.controller = ConnectMenuController.ConnectMenuController(self.main)
			self.main.controller.message_element.set_text(self.main.client.connection_status)
		self.main.main_element.set_text(self.current_message)