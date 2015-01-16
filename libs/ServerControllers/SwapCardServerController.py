from ServerController import ServerController
from ..Deck import *
from ..CardTable import xcoords_to_index
from ..HistoryMachine import SNAPSHOT_SWAP_CARD
import time, random

class SwapCardServerController(ServerController):
	#This controller receives a card that the player wants to play.
	#It then waits for the player to pick a location on the grid to play it at.
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
							#we attempt to swap this card from the player's hand.
							self.gameserver.history.take_snapshot(SNAPSHOT_SWAP_CARD, player.name+" swapped '"+self.selected_card.name+"' with '"+selected_card.name+"'.")
							self.gameserver.send_full_history_all()
							self.gameserver.server.sendall("ALERT:draw_card_from_table")
							self.gameserver.server.sendall("ALERT:add_card_to_table")
							self.gameserver.server.sendall("ALERT:add_card_to_table")
							if self.selected_card.temp_card_being_imitated != None:
								self.selected_card.reset()
							if selected_card.temp_card_being_imitated != None:
								selected_card.reset()
							self.gameserver.card_table.pony_cards[location[1]][location[0]] = self.selected_card
							self.gameserver.card_table.pony_cards[self.selected_card_location[1]][self.selected_card_location[0]] = selected_card
							self.gameserver.last_card_table_offset = self.gameserver.card_table.refactor() #Pointless, but I'm doing it anyways.
							self.gameserver.send_cardtable_all()
						else:
							self.gameserver.server.sendto(player.address,"ADD_CHAT:SERVER:PM:You can not swap this card!")
					else:
						print "ERROR! Something was wrong with this card's id."
					self.gameserver.controller = None
				else:
					self.gameserver.server.sendto(player.address,"ADD_CHAT:SERVER:PM:It's not your turn, you can't swap a card right now!")
			else:
				self.gameserver.server.sendto(player.address,"ADD_CHAT:SERVER:PM:You can't swap a card, the game hasn't started...")
		else:
			return False
		return True

