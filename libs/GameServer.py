import Deck
import netcom
from locals import *
import thread
import time

GAMESTAGE_INIT = -1  # The server hasn't been started yet.
GAMESTAGE_PREGAME = 0  # The game hasn't started yet, but the server is accepting players.
GAMESTAGE_GAMEPREP = 1  # The game will begin soon - every player needs to receive all game resources.

class Player(object):
	def __init__(self,address,name):
		self.address = address
		self.name = name
		self.hand = Deck.Deck()

		self.is_pinged = False


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
		self.stage = GAMESTAGE_INIT
		self.last_updated_playerlist = 0
		print "= Waiting for 'run_main_loop' to be called."
		print

	def run_main_loop(self):
		# Call this function to get the server running.
		print "= 'run_main_loop' called..."
		self.stage = GAMESTAGE_PREGAME
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
		#TODO: Finish _update command.
		if self.stage == GAMESTAGE_PREGAME:
			t = time.time()
			if t - self.last_updated_playerlist > 1:
				self.last_updated_playerlist = t
				# Check if any players have connected
				for key in self.server.clients.keys():
					match = False
					for player in self.players:
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
				keys = self.server.clients.keys()
				i = len(self.players) - 1
				while i >= 0:
					player = self.players[i]
					if player.address not in keys:
						#Player has disconnected
						print "=Player '"+player.name+"'", player.address, "has left the game."
						self.server.sendall("ADD_CHAT:"+"Player '"+player.name+"' has left.")
						#TODO: Do proper cleanup for disconnected players.
						del self.players[i]
						self.send_playerlist()
					i -= 1
			for key in self.server.clients.keys():
				if len(self.server.received_messages[key]) > 0:
					message = self.server.received_messages[key].pop(0)
					if message.startswith("CONNECT:"):
						#We get the clients name now and add them to the game.
						#TODO: Kick the client if their name sucks.
						if False:
							pass
						else:
							name = message[len("CONNECT:"):]
							self.players.append(Player(key, name))
							self.server.sendto(key,"CONNECTED")
							print "=Player '"+name+"'", key, "has joined the game."
							self.server.sendall("ADD_CHAT:"+"Player '"+name+"' has joined.")
							self.send_playerlist()
					elif message.startswith("CHAT:"):
						player = None
						for pl in self.players:
							if pl.address == key:
								player = pl
								break
						if not player:
							name = "UNKNOWN"
						else:
							name = player.name
						chat = message[len("CHAT:"):]
						self.server.sendall("ADD_CHAT:"+name+": "+chat)
	
	def _read_messages(self):
		#TODO: Do _read_messages command.
		pass

	def _check_player_status(self):
		# This function is to check that players are still connected, otherwise it kicks them after no response.
		t = time.time()
		player_list = list(self.players)
		for player in player_list:
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
				self.send_playerlist()
				#TODO: send message to remaining clients to let them know about the updated player list.

	def send_playerlist(self):
		s = "PLAYERLIST:"
		i = 0
		while i < len(self.players):
			s += self.players[i].name
			if i != len(self.players)-1:
				s += ","
			i += 1



