from ServerController import ServerController

from ..ServerPlayer import Player
from ..locals import *

import time

class ServerGameStartingController(ServerController):
	def init(self):
		for player in self.gameserver.players:
			player.is_ready = False
		self.players_ready = 0
		self.last_updated_playerlist = 0
		self.gameserver.server.sendall("BEGIN_LOAD")

	def update(self):
		t = time.time()
		if t - self.last_updated_playerlist > 1:
			self.last_updated_playerlist = t
			# Check if any players have connected
			for key in self.gameserver.server.clients.keys():
				match = False
				for player in self.gameserver.players:
					if player.address == key:
						match = True
						break
				if not match:
					#TODO: Kick them if the server is full or they're banned
					if False:
						pass
					else:
						#This player is attempting to connect, we need to receive a CONNECT request before we continue.
						pass
			# Check if any players have disconnected
			keys = self.gameserver.server.clients.keys()
			i = len(self.gameserver.players) - 1
			while i >= 0:
				player = self.gameserver.players[i]
				if player.address not in keys:
					#Player has disconnected
					print "=Player '"+player.name+"'", player.address, "has left the game."
					self.gameserver.server.sendall("ADD_CHAT:SERVER:"+"Player '"+player.name+"' has disconnected?")
					self.gameserver.players.pop(i)
					self.send_playerlist()
				i -= 1

		if self.players_ready == len(self.gameserver.players):
			self.gameserver.server.sendall("GAME_START")

	def read_messages(self):
		for key in self.gameserver.server.clients.keys():
			message = None
			player = None
			for pl in self.gameserver.players:
				if pl.address == key:
					player = pl
					break
			try:
				if len(self.gameserver.server.received_messages[key]) > 0:
					message = self.gameserver.server.received_messages[key].pop(0)
			except:
				print "= FAILED TO POP AT KEY:",key
			if message != None:
				print message[:100]
				if message == PING_MESSAGE:
					self.gameserver.server.sendto(key,PONG_MESSAGE)
				elif message == "REQUEST_DECKSIZE":
					self.gameserver.server.sendto(key,"DECKSIZE:"+str(len(self.gameserver.master_deck.cards)))
				elif message.startswith("REQUEST_CARDFILE:"):
					index = int(message[len("REQUEST_CARDFILE:"):])
					data = "CARDFILE:"+str(index)+":"+self.gameserver.master_deck.pc_cards[index]
					print "SENDING CARD: "+data[:100]
					self.gameserver.server.sendto(key,data)
				elif message == "DONE_AND_WAITING":
					if not player.is_ready:
						player.is_ready = True
						self.players_ready += 1

	def check_player_status(self):
		# This function is to check that players are still connected, otherwise it kicks them after no response.
		t = time.time()
		player_list = list(self.gameserver.players)
		for player in player_list:
			pa = player.address
			pn = player.name

			kick_em = False
			# First we check if the player is even still in the server's client listing.
			if pa in self.gameserver.server.clients:
				#Next we check when we last received a message from that client.
				try:
					lgm = self.gameserver.server.client_last_got_message[pa]
					dif = t - lgm
					if dif >= PING_FREQUENCY:
						if not player.is_pinged:
							player.is_pinged = True
							self.gameserver.server.sendto(pa,PING_MESSAGE)
						else:
							# This means the player was already sent a 'ping', and we're waiting for a 'pong'
							if dif >= PING_FREQUENCY + TIMEOUT_TIME:
								#This player has timed out, so we must kick them.
								print "= Client '"+pn+"' has timed-out from '"+pa+"'"
								kick_em = True
					else:
						# This player is likely still connected.
						player.is_pinged = False
				except:
					print "= FAILED TO CHECK ON AND/OR PING PLAYER '"+pn+"' AT '"+pa+"'"
			else:
				print "= Client '"+pn+"' has disconnected from '"+pa+"'"
				kick_em = True
			if kick_em:
				print "= Player '"+pn+"' has been kicked."
				self.gameserver.server.disconnect(pa)
				self.gameserver.players.remove(player)
