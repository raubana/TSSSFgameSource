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
			# We are in the pregame stage.
			pass

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
						if player.is_pinged:
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
				print "= Player '"+pn+"' has disconnected."
				#TODO: Close connection between the server and this client.
				#TODO: Remove this player from the
				#TODO: update players list and reassign whose turn it is, if necessary.
				#TODO: send message to remaining clients to let them know about the updated player list.



