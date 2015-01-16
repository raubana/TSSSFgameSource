from ServerController import ServerController
from ..Deck import *
from ..CardTable import xcoords_to_index
from ..HistoryMachine import SNAPSHOT_REPLACED_CARD
import time, random

class ReplaceCardServerController(ServerController):
	#This controller receives a card that the player wants to play.
	#It then waits for the player to pick a card on the grid to replace.
	def init(self):
		self.selected_card = None

	def update(self):
		pass

	def read_message(self, message, player):
		if message.startswith("CLICKED_CARD:"):
			#we play the selected card.
			if self.gameserver.game_started:
				if self.gameserver.players.index(player) == self.gameserver.current_players_turn:
					#we check if this card is in the player's hand.
					s = message[len("CLICKED_CARD:"):]
					try:
						i = int(s)
						works = True
					except:
						works = False
					if works:
						location = None
						#only pony cards can be replaced, so we search through the pony cards on the shipping grid.
						for y in xrange(self.gameserver.card_table.size[1]):
							for x in xrange(self.gameserver.card_table.size[0]):
								card = self.gameserver.card_table.pony_cards[y][x]
								if card != None:
									if self.gameserver.master_deck.cards.index(card) == i:
										location = (x,y)
										selected_card = card
										break
							if location != None:
								break
						if location != None:
							if selected_card.type == "pony" and selected_card.power == "startcard":
								self.gameserver.server.sendto(player.address,"ADD_CHAT:SERVER:PM:You can't replace the start card!")
							else:
								#we attempt to discard this card from the player's hand.
								self.gameserver.history.take_snapshot(SNAPSHOT_REPLACED_CARD, player.name+" replaced '"+selected_card.name+"' with '"+self.selected_card.name+"'.")
								self.gameserver.send_full_history_all()
								self.gameserver.server.sendall("ALERT:draw_card_from_table")
								self.gameserver.server.sendall("ALERT:add_card_to_table")
								self.gameserver.server.sendall("ALERT:add_card_to_deck")
								player.hand.remove_card(self.selected_card)
								self.gameserver.pony_discard.add_card_to_top(selected_card)
								self.gameserver.card_table.pony_cards[location[1]][location[0]] = self.selected_card
								self.gameserver.last_card_table_offset = self.gameserver.card_table.refactor() #Pointless, but I'm doing it anyways.
								self.gameserver.send_decks_all()
								self.gameserver.send_cardtable_all()
								self.gameserver.send_playerhand(player)
						else:
							self.gameserver.server.sendto(player.address,"ADD_CHAT:SERVER:PM:You can not replace this card!")
					else:
						print "ERROR! Something was wrong with this card's id."
					self.gameserver.controller = None
				else:
					self.gameserver.server.sendto(player.address,"ADD_CHAT:SERVER:PM:It's not your turn, you can't replace a card right now!")
			else:
				self.gameserver.server.sendto(player.address,"ADD_CHAT:SERVER:PM:You can't replace a card, the game hasn't started...")
		else:
			return False
		return True

