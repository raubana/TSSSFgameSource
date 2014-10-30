from ServerController import ServerController
from ..Deck import *
from ..CardTable import xcoords_to_index
from ..HistoryMachine import SNAPSHOT_DREW_PONY_CARD, SNAPSHOT_DREW_SHIP_CARD
import time, random

class DrawFromDiscardsServerController(ServerController):
	#This controller receives a card that the player wants to play.
	#It then waits for the player to pick a location on the grid to play it at.

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
						if selected_card in self.gameserver.pony_discard.cards:
							#we attempt to swap this card from the player's hand.
							self.gameserver.history.take_snapshot(SNAPSHOT_DREW_PONY_CARD, player.name+" searched through and drew '"+selected_card.name+"' from the Pony discard pile.")
							self.gameserver.send_full_history_all()
							self.gameserver.server.sendall("ALERT:draw_card_from_deck")
							self.gameserver.pony_discard.remove_card(selected_card)
							self.gameserver.server.sendall("ALERT:add_card_to_hand")
							player.hand.add_card_to_top(selected_card)
							self.gameserver.send_playerhand(player)
							self.gameserver.send_decks_all()
						elif selected_card in self.gameserver.ship_discard.cards:
							#we attempt to swap this card from the player's hand.
							self.gameserver.history.take_snapshot(SNAPSHOT_DREW_SHIP_CARD, player.name+" searched through and drew '"+selected_card.name+"' from the Ship discard pile.")
							self.gameserver.send_full_history_all()
							self.gameserver.server.sendall("ALERT:draw_card_from_deck")
							self.gameserver.ship_discard.remove_card(selected_card)
							self.gameserver.server.sendall("ALERT:add_card_to_hand")
							player.hand.add_card_to_top(selected_card)
							self.gameserver.send_playerhand(player)
							self.gameserver.send_decks_all()
						else:
							self.gameserver.server.sendto(player.address,"ADD_CHAT:SERVER:PM:You can draw this card!")
					else:
						print "ERROR! Something was wrong with this card's id."
					if self.gameserver.controller:
						self.gameserver.controller.cleanup()
						self.gameserver.controller = None
				else:
					self.gameserver.server.sendto(player.address,"ADD_CHAT:SERVER:PM:It's not your turn, you can't draw from discard right now!")
			else:
				self.gameserver.server.sendto(player.address,"ADD_CHAT:SERVER:PM:You can't draw from discards, the game hasn't started...")
			self.cleanup()
		else:
			return False
		return True

