from ServerController import ServerController

from ..ServerPlayer import Player
from ..locals import *
from ..CardTable import*
from ..Deck import Deck

import time

class ServerGameController(ServerController):
	def init(self):
		print "=Preparing the game..."
		#first we create out card table
		print "== creating card table..."
		self.gameserver.grid = CardTable()
		#next we create our locations for our cards
		self.gameserver.pony_deck = Deck()
		self.gameserver.pony_discard_pile = Deck()
		self.gameserver.ship_deck = Deck()
		self.gameserver.ship_discard_pile = Deck()
		self.gameserver.goal_deck = Deck()
		self.gameserver.public_goals = Deck()
		#next we sort out our cards...
		print "== sorting cards..."
		for card in self.gameserver.master_deck.cards:
			if card.type == "pony": self.gameserver.pony_deck.add_card_to_bottom(card)
			elif card.type == "ship": self.gameserver.ship_deck.add_card_to_bottom(card)
			elif card.type == "goal": self.gameserver.goal_deck.add_card_to_bottom(card)
			else: print "ERROR! Card of unknown type in the deck:", card.type
		#... and shuffle the decks
		print "== shuffling decks..."
		self.gameserver.pony_deck.shuffle()
		self.gameserver.ship_deck.shuffle()
		self.gameserver.goal_deck.shuffle()
		#next we give each player the required number of cards
		print "== drawing to give players their starting hands..."
		#TODO: Make sure we get these cards back should we remove this player from the game
		for player in self.gameserver.players:
			for i in xrange(4):
				player.hand.add_card_to_bottom(self.gameserver.pony_deck.draw_card())
			for i in xrange(3):
				player.hand.add_card_to_bottom(self.gameserver.ship_deck.draw_card())
		#next we draw the first 3 public goals
		print "== drawing public goals..."
		for i in xrange(3):
			self.gameserver.public_goals.append(self.gameserver.goal_deck.draw_card())
		#TODO: Don't forget to assign who gets first turn
		#finally we inform our clients that the game is now ready
		self.gameserver.server.sendall("GAME_START")

	def read_message(self, message, player):
		return False