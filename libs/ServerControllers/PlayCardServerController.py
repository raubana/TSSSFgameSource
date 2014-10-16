from ServerController import ServerController
from ..Deck import *
import time, random

class PlayCardServerController(ServerController):
	#This controller receives a card that the player wants to play.
	#It then waits for the player to pick a location on the grid to play it at.
	def init(self):
		self.selected_card = None
		self.location_type = "pony"

	def update(self):
		pass

	def read_message(self, message, player):
		if message.startswith("CLICKED_GRID_AT:"):
			#we play the selected card.
			if self.gameserver.game_started:
				if self.gameserver.players.index(player) == self.gameserver.current_players_turn:
					#we check if this card is in the player's hand.
					s = message[len("CLICKED_GRID_AT:"):]
					parts = s.split(",")
					if len(parts) == 2:
						try:
							x = int(parts[0])
							y = int(parts[1])
							works = True
						except:
							works = False
						if works:
							#we check if this position is legal on the grid.
							if self.gameserver.card_table.check_if_legal_index((x,y),self.location_type):
								#we remove the card from the players hand and then add the card to the shipping grid.
								player.hand.remove_card(self.selected_card)
								if self.location_type == "pony":
									self.gameserver.card_table.pony_cards[y][x] = self.selected_card
								elif self.location_type == "v_ship":
									self.gameserver.card_table.v_ship_cards[y][x] = self.selected_card
								elif self.location_type == "h_ship":
									self.gameserver.card_table.h_ship_cards[y][x] = self.selected_card
								self.gameserver.card_table.refactor()
								self.gameserver.server.sendall("ALERT:add_card_to_table")
								self.gameserver.setTimerDuration(SERVER_TURN_MAX_DURATION)
								#finally, we send the player their new hand and we send all players the new table.
								self.gameserver.send_playerhand(player)
								self.gameserver.send_cardtable_all()
								self.gameserver.controller = None
							else:
								self.gameserver.server.sendto(player.address,"ADD_CHAT:SERVER:You can't put this card here!")
								self.gameserver.controller = None
				else:
					self.gameserver.server.sendto(player.address,"ADD_CHAT:SERVER:It's not your turn, you can't play a card right now!")
			else:
				self.gameserver.server.sendto(player.address,"ADD_CHAT:SERVER:You can't play a card, the game hasn't started...")
		else:
			return False
		return True

