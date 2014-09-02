import Deck
import netcom
from locals import *
import thread
import time

from libs.ServerControllers import PreGameController
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
		self.stage = PreGameController.PreGameController(self)
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
		self.controller.update()

	def _read_messages(self):
		self.controller.read_messages()

	def _check_player_status(self):
		self.controller.check_player_status()



