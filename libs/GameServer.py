import Deck
import netcom
from locals import *
import thread
import time

from ServerPlayer import Player
import CustomDeck
from PickledCard import open_pickledcard

class GameServer(object):
	def __init__(self, port=DEFAULT_PORT):
		print "= GameServer initializing..."
		self.port = port
		# First we need to load the deck
		print "= Waiting for 'run_main_loop' to be called."
		print
		self.controller = None
		self.server = None

		self.players = []

		self.load_custom_deck()

		self.reset()

	def reset(self):
		self.game_started = False
		self.begun_gamestart_countdown = False
		self.gamestart_countdown = 10
		self.gamestart_countdown_time = 0
		for pl in self.players:
			pl.reset()
		if self.server != None:
			self.send_playerlist()

	def load_custom_deck(self):
		print "== loading the MasterDeck"
		self.master_deck = Deck.MasterDeck()
		self.custom_deck = CustomDeck.CustomDeck()
		try:
			f = open("your_deck.txt")
		except:
			print("Couldn't find 'your_deck.txt' so we're going to load the default cards only.")
			self.master_deck.load_all_cards()
			return
		instr = f.read()
		f.close()
		print
		print " --- READING CUSTOM DECK INSTRUCTIONS --- "
		print
		self.custom_deck.follow_instructions(instr)
		print
		print " --- DONE --- "
		print
		print "=== loading cards..."
		pc_list = []
		defaults = os.listdir("data/default_cards")
		for card in self.custom_deck.list:
			if card.startswith("R:"):
				pc = open_pickledcard("cards/"+card[2:])
			else:
				if card in defaults:
					pc = open_pickledcard("data/default_cards/"+card)
				else:
					pc = open_pickledcard("cards/"+card)
			pc_list.append(pc)
		self.master_deck.load_all_cards(pc_list)
		print "== MasterDeck loaded."

	def run_main_loop(self):
		# Call this function to get the server running.
		print "= 'run_main_loop' called..."
		print "== starting server now..."
		self.server = netcom.Server(netcom.gethostname(), self.port)
		print "== the server should now operational."
		thread.start_new_thread(self._run(), tuple([]))

	def _run(self):
		# This is the main loop for the entire GameServer class.
		self.running = True
		while self.running:
			self._update()
			self._read_messages()
			self._check_player_status()

	def _update(self):
		t = time.time()
		if not self.game_started:
			if self.begun_gamestart_countdown:
				if t - self.gamestart_countdown_time >= 1:
					if self.gamestart_countdown <= 0:
						import libs.ServerControllers.SetupNewgameServerController as SetupNewgameServerController
						self.controller = SetupNewgameServerController.SetupNewgameServerController(self)
					else:
						self.server.sendall("ADD_CHAT:SERVER:..."+str(self.gamestart_countdown)+"...")
						self.server.sendall("ALERT:game_timer")
						self.gamestart_countdown -= 1
						self.gamestart_countdown_time = t

		if self.controller != None:
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
					#TODO: Kick the client if their name sucks or if the game's already started
					if self.game_started:
						self.server.kick(key,"The game's already started. Please come back later.")
					else:
						data = message[len("CONNECT:"):]
						data = data.split(":")
						if len(data) < 2:
							self.server.kick(key,"You seem to be running an older version. Please go updated.")
						else:
							player_key = data[0]
							name = data[1]
							if player == None:
								for pl in self.players:
									if pl.name == name and pl.player_key == player_key:
										player = pl
										break
							if player != None:
								#reconnect player
								if not player.is_connected:
									self.server.sendto(key,"CONNECTED:"+name)
									self.server.sendall("ADD_CHAT:SERVER:"+"Player '"+name+"' has reconnected.")
									player.is_connected = True
									player.address = key
									if self.controller != None:
										self.controller.triggerRejoinPlayer(player)
									print "=Player '"+name+"'", key, "has rejoined the game."
								else:
									#we kick this one, since the player is already connected.
									self.server.kick(key,"This player is already connected.")
							else:
								#connect new player
								self.server.sendto(key,"CONNECTED:"+name)
								self.server.sendall("ADD_CHAT:SERVER:"+"Player '"+name+"' has connected.")
								self.players.append(Player(key, name, player_key))
								if self.controller != None:
									self.controller.triggerNewPlayer(self.players[-1])
								print "=Player '"+name+"'", key, "has joined the game."
							self.send_playerlist()
							self.check_ready()
				elif message.startswith("CHAT:"):
					if not player:
						name = "???"
					else:
						name = player.name
					chat = message[len("CHAT:"):]
					self.server.sendall("ADD_CHAT:PLAYER:"+name+": "+chat)
				elif message == "REQUEST_DECK":
					s = ""
					i = 0
					while i < len(self.custom_deck.list):
						card = self.custom_deck.list[i]
						if card.startswith("R:"):
							card = card[2:]
						s += card
						i += 1
						if i < len(self.custom_deck.list):
							s += ","
					self.server.sendto(player.address,"DECK:"+s)
				elif message.startswith("REQUEST_CARDFILE:"):
					index = int(message[len("REQUEST_CARDFILE:"):])
					data = "CARDFILE:"+str(index)+":"+self.master_deck.pc_cards[index]
					#print "SENDING CARD: "+data[:100]
					self.server.sendto(player.address,data)
				elif message.startswith("REQUEST_CARDFILE_ATTRIBUTES:"):
					index = int(message[len("REQUEST_CARDFILE_ATTRIBUTES:"):])
					data = "CARDFILE_ATTRIBUTES:"+str(index)+":"+self.master_deck.cards[index].attributes
					#print "SENDING CARD ATTRIBUTES: "+data[:100]
					self.server.sendto(player.address,data)
				elif message == "DONE_LOADING":
					player.is_loaded = True
					self.server.sendto(player.address, "CLIENT_READY")
					self.server.sendall("ADD_CHAT:SERVER:"+"Player '"+player.name+"' has joined.")
					self.send_playerlist()
					self.check_ready()
				elif not self.game_started and message == "READY":
					#toggle this player's "is_ready" variable
					t = time.time()
					if t - player.last_toggled_ready < 3:
						self.server.sendto(player.address,"ADD_CHAT:SERVER:You're doing that too often.")
					else:
						player.is_ready = not player.is_ready
						player.last_toggled_ready = t
						if player.is_ready:
							self.server.sendall("ADD_CHAT:SERVER:"+"Player '"+player.name+"' is ready.")
							self.server.sendall("ALERT:player_ready")
						else:
							self.server.sendall("ADD_CHAT:SERVER:"+"Player '"+player.name+"' is NOT ready.")
							self.server.sendall("ALERT:player_not_ready")
						self.send_playerlist()
						self.check_ready()
				else:
					if self.controller != None:
						attempt = self.controller.read_message(message, player)
						if not attempt:
							print "ERROR: Received unknown message: "+message[:100]
					else:
						print "ERROR: Received unknown message and no controller: "+message[:100]

	def _check_player_status(self):
		# This function is to check that players are still connected, otherwise it kicks them after no response.
		t = time.time()
		i = len(self.players)-1
		while i >= 0:
			player = self.players[i]
			pa = player.address
			pn = player.name
			if player.is_connected:
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
					self.server.kick(pa)
					player.is_connected = False
					player.is_ready = False
					player.time_of_disconnect = time.time()
					self.server.sendall("ADD_CHAT:SERVER:"+"Player '"+player.name+"' has disconnected.")
					if self.controller != None:
						self.controller.triggerPlayerDisconnect(player)
					self.send_playerlist()
					self.check_ready()
			else:
				if not self.game_started or t - player.time_of_disconnect >= 60:
					#TODO: Discard player's hand
					#TODO: Check if the game needs to reset
					#TODO: Check if it was this player's turn. If it was, change whose turn it is
					self.server.sendall("ADD_CHAT:SERVER:"+"Player '"+player.name+"' has been removed from the game.")
					del self.players[i]
					self.send_playerlist()
					self.check_ready()
			i -= 1

	def check_ready(self):
		if not self.game_started:
			number_ready = 0
			for player in self.players:
				if player.is_connected and player.is_ready:
					number_ready += 1

			ready = number_ready >= MIN_PLAYERS and number_ready == len(self.players)

			if ready and not self.begun_gamestart_countdown:
				self.gamestart_countdown = 10
				self.gamestart_countdown_time = time.time()
				self.begun_gamestart_countdown = True
				self.server.sendall("ADD_CHAT:SERVER: The game will start in...")
			elif not ready and self.begun_gamestart_countdown:
				self.begun_gamestart_countdown = False
				self.server.sendall("ADD_CHAT:SERVER: ...Aborted.")

	def send_playerlist(self):
		s = "PLAYERLIST:"
		i = 0
		while i < len(self.players):
			player = self.players[i]
			if not player.is_connected:
				s += "DC:"
			if not self.game_started:
				if player.is_ready:
					s += "R:"
				else:
					s += "NR:"
			if not player.is_loaded:
				s += "L:"
			s += player.name
			if i != len(self.players)-1:
				s += ","
			i += 1
		self.server.sendall(s)