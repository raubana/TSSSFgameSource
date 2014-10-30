from ServerController import ServerController
from ..Deck import *
from ..CardTable import xcoords_to_index
from ..HistoryMachine import SNAPSHOT_IMITATE_CARD
import time, random

class ImitateCardServerController(ServerController):
	#This controller receives a card that the player wants to play.
	#It then waits for the player to pick a location on the grid to play it at.
	def init(self):
		self.selected_card = None
		self.selected_card_location = None

		if self.gameserver.current_players_turn != None:
			deck = Deck()
			for card in self.gameserver.master_deck.cards:
				if card.type == "pony":
					deck.add_card_to_bottom(card)
			player = self.gameserver.players[self.gameserver.current_players_turn]
			self.gameserver.send_card_selection_player(player,deck)

	def cleanup(self):
		if self.gameserver.current_players_turn != None:
			deck = Deck()
			player = self.gameserver.players[self.gameserver.current_players_turn]
			self.gameserver.send_card_selection_player(player,deck)

	def update(self):
		pass

	def read_message(self, message, player):
		if message.startswith("CLICKED_CARD:"):
			#we play the selected card.
			if self.gameserver.game_started:
				if self.gameserver.players.index(player) == self.gameserver.current_players_turn:
					#we check if this card is imitate-able.
					s = message[len("CLICKED_CARD:"):]
					try:
						i = int(s)
						works = True
					except:
						works = False
					if works:
						selected_card = self.gameserver.master_deck.cards[i]
						if selected_card.type == "pony":
							#we attempt to swap this card from the player's hand.
							self.gameserver.history.take_snapshot(SNAPSHOT_IMITATE_CARD, player.name+" made '"+self.selected_card.name+"' imitate '"+selected_card.name+"'.")
							self.gameserver.send_full_history_all()
							self.gameserver.server.sendall("ALERT:imitate_card")
							self.selected_card.imitate_card(selected_card, self.gameserver.master_deck)
							self.gameserver.send_cardtable_all()
						else:
							self.gameserver.server.sendto(player.address,"ADD_CHAT:SERVER:PM:You can not imitate this card!")
					else:
						print "ERROR! Something was wrong with this card's id."
					self.gameserver.controller = None
				else:
					self.gameserver.server.sendto(player.address,"ADD_CHAT:SERVER:PM:It's not your turn, you can't make a card imitate right now!")
			else:
				self.gameserver.server.sendto(player.address,"ADD_CHAT:SERVER:PM:You can't make a card imitate, the game hasn't started...")
			self.cleanup()
		else:
			return False
		return True

