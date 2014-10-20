from ServerController import ServerController
from ..Deck import *
from ..CardTable import xcoords_to_index
from ..HistoryMachine import SNAPSHOT_PLAY_CARD
import time, random

class PlayCardServerController(ServerController):
	#This controller receives a card that the player wants to play.
	#It then waits for the player to pick a location on the grid to play it at.
	def init(self):
		self.selected_card = None

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
							info = xcoords_to_index((x,y),self.selected_card.type)
							index = info[1]
							is_legal = False
							if info[0] == "pony":
								if self.gameserver.card_table.check_if_legal_index(index,"pony"):
									self.gameserver.card_table.pony_cards[index[1]][index[0]] = self.selected_card
									is_legal = True
							elif info[0] == "h ship":
								if self.gameserver.card_table.check_if_legal_index(index,"h ship"):
									self.gameserver.card_table.h_ship_cards[index[1]][index[0]] = self.selected_card
									is_legal = True
							elif info[0] == "v ship":
								if self.gameserver.card_table.check_if_legal_index(index,"v ship"):
									self.gameserver.card_table.v_ship_cards[index[1]][index[0]] = self.selected_card
									is_legal = True

							if is_legal:
								self.gameserver.history.take_snapshot(SNAPSHOT_PLAY_CARD, player.name+" placed the card '"+self.selected_card.name+"' onto the shipping grid.")
								self.send_full_history_all()
								player.hand.remove_card(self.selected_card)
								#we remove the card from the players hand and then add the card to the shipping grid.
								self.gameserver.card_table.refactor()
								self.gameserver.server.sendall("ALERT:add_card_to_table")
								self.gameserver.setTimerDuration(SERVER_TURN_MAX_DURATION)
								#finally, we send the player their new hand and we send all players the new table.
								self.gameserver.send_playerhand(player)
								self.gameserver.send_cardtable_all()
							else:
								self.gameserver.server.sendto(player.address,"ADD_CHAT:SERVER:You can't put this card here!")
								self.gameserver.server.sendall("ALERT:add_card_to_hand")
							self.gameserver.controller = None
				else:
					self.gameserver.server.sendto(player.address,"ADD_CHAT:SERVER:It's not your turn, you can't play a card right now!")
			else:
				self.gameserver.server.sendto(player.address,"ADD_CHAT:SERVER:You can't play a card, the game hasn't started...")
		else:
			return False
		return True

