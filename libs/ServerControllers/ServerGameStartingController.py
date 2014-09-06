from ServerController import ServerController

from ..ServerPlayer import Player
from ..locals import *

import time

class ServerGameStartingController(ServerController):
	def init(self):
		for player in self.gameserver.players:
			player.is_ready = False
		self.players_ready = 0
		self.gameserver.server.sendall("BEGIN_LOAD")

	def update(self):
		if self.players_ready == len(self.gameserver.players):
			import ServerGameController
			self.gameserver.controller = ServerGameController.ServerGameController(self.gameserver)

	def read_message(self, message, player):
		#print message[:100]
		if message == "REQUEST_DECKSIZE":
			self.gameserver.server.sendto(player.address,"DECKSIZE:"+str(len(self.gameserver.master_deck.cards)))
		elif message.startswith("REQUEST_CARDFILE:"):
			index = int(message[len("REQUEST_CARDFILE:"):])
			data = "CARDFILE:"+str(index)+":"+self.gameserver.master_deck.pc_cards[index]
			print "SENDING CARD: "+data[:100]
			self.gameserver.server.sendto(player.address,data)
		elif message == "DONE_AND_WAITING":
			if not player.is_ready:
				player.is_ready = True
				self.players_ready += 1
		else:
			return False
		return True
