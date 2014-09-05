import Deck
import netcom
from locals import *
import thread
import time

from libs.ServerControllers import ServerPreGameController
from ServerPlayer import Player

class GameServer(object):
	def __init__(self, port=DEFAULT_PORT):
		print "= GameServer initializing..."
		self.port = port
		# First we need to load the deck
		print "== loading the MasterDeck"
		self.master_deck = Deck.MasterDeck()
		self.master_deck.load_all_cards()  # Each game server will have only one deck for the duration of it's existence
		print "== the MasterDeck is now fully loaded."
		self.players = []
		print "= Waiting for 'run_main_loop' to be called."
		print
		self.controller = None

	def run_main_loop(self):
		# Call this function to get the server running.
		print "= 'run_main_loop' called..."
		print "== starting server now..."
		self.server = netcom.Server(netcom.gethostname(), self.port)
		print "== the server should now operational."
		self.controller = ServerPreGameController.ServerPreGameController(self)
		thread.start_new_thread(self._run(), tuple([]))

	def _run(self):
		# This is the main loop for the entire GameServer class.
		self.running = True
		while self.running:
			self._update()
			self._read_messages()
			self._check_player_status()

	def _update(self):
		self.controller.update()

	def _read_messages(self):
		for key in self.server.clients.keys():
			message = None
			player = None
			for pl in self.players:
				if pl.address == key:
					player = pl
					break
			try:
				if len(self.server.received_messages[key]) > 0:
					message = self.server.received_messages[key].pop(0)
			except:
				print "= FAILED TO POP AT KEY:",key

			if message != None:
				if message == PING_MESSAGE:
					self.server.sendto(key,PONG_MESSAGE)
				elif message == PONG_MESSAGE:
					pass
				elif message.startswith("CONNECT:"):
					#We get the clients name now and add them to the game.
					#TODO: Kick the client if their name sucks.
					if False:
						pass
					else:
						name = message[len("CONNECT:"):]
						self.server.sendto(key,"CONNECTED")
						self.server.sendall("ADD_CHAT:SERVER:"+"Player '"+name+"' has joined.")
						if player != None:
							#reconnect player
							self.controller.triggerRejoinPlayer(player)
							print "=Player '"+name+"'", key, "has rejoined the game."
						else:
							#connect new player
							self.players.append(Player(key, name))
							self.controller.triggerNewPlayer(self.players[-1])
							print "=Player '"+name+"'", key, "has joined the game."
						self.send_playerlist()
				elif message.startswith("CHAT:"):
					if not player:
						name = "???"
					else:
						name = player.name
					chat = message[len("CHAT:"):]
					self.server.sendall("ADD_CHAT:PLAYER:"+name+": "+chat)
				else:
					attempt = self.controller.read_message(message, player)
					if not attempt:
						print "ERROR: Received unknown message: "+message[:100]

	def _check_player_status(self):
		# This function is to check that players are still connected, otherwise it kicks them after no response.
		t = time.time()
		i = len(self.players)-1
		while i >= 0:
			player = self.players[i]
			pa = player.address
			pn = player.name
			kick_em = False
			# First we check if the player is even still in the server's client listing.
			if pa in self.server.clients:
				#Next we check when we last received a message from that client.
				try:
					lgm = self.server.client_last_got_message[pa]
					dif = t - lgm
					if dif >= PING_FREQUENCY:
						if not player.is_pinged:
							player.is_pinged = True
							self.server.sendto(pa,PING_MESSAGE)
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
				self.server.disconnect(pa)
				self.players.remove(player)
				self.server.sendall("ADD_CHAT:SERVER:"+"Player '"+player.name+"' has disconnected.")
				self.server.sendall("ALERT_NOT_READY")
				self.controller.triggerPlayerDisconnect(player)
				self.send_playerlist()
			i -= 1

	def send_playerlist(self):
		s = "PLAYERLIST:"
		i = 0
		while i < len(self.players):
			s += self.players[i].name
			if i != len(self.players)-1:
				s += ","
			i += 1
		self.server.sendall(s)