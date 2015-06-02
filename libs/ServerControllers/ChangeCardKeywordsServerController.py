from ServerController import ServerController
from ..Deck import *
from ..CardTable import xcoords_to_index
from ..HistoryMachine import SNAPSHOT_NULL
import time, random

class ChangeCardKeywordsServerController(ServerController):
	#This controller receives a card that the player wants to change.
	#It then waits for the player to type the new keywords into the chat.
	def init(self):
		self.selected_card = None

	def update(self):
		pass

	def cleanup(self):
		if self.gameserver.current_players_turn != None:
			deck = Deck()
			player = self.gameserver.players[self.gameserver.current_players_turn]
			self.gameserver.send_card_selection_player(player,deck)

	def read_message(self, message, player):
		if message.startswith("EDIT_KEYWORDS:"):
			if self.gameserver.game_started:
				if self.gameserver.players.index(player) == self.gameserver.current_players_turn:
					#we check if this card is in the player's hand.
					print message
					s = message[len("EDIT_KEYWORDS:"):]
					location = None
					#only pony cards can have their keywords changed, so we search through the pony cards on the shipping grid.
					for y in xrange(self.gameserver.card_table.size[1]):
						for x in xrange(self.gameserver.card_table.size[0]):
							card = self.gameserver.card_table.pony_cards[y][x]
							if card != None:
								if card == self.selected_card:
									location = (x,y)
									selected_card = card
									break
						if location != None:
							break
					if location != None:
						#we attempt to discard this card from the player's hand.
						self.selected_card.set_temp_keywords(string.split(s,","))
						self.gameserver.history.take_snapshot(SNAPSHOT_NULL, player.name+" changed '"+selected_card.name+"' keywords to '"+str(self.selected_card.temp_keywords)+"'.")
						self.gameserver.server.sendall("ALERT:added_keywords")
						self.gameserver.send_full_history_all()
					else:
						self.gameserver.server.sendto(player.address,"ADD_CHAT:SERVER:PM:You can not change this card's keywords!")
					self.gameserver.controller = None
				else:
					self.gameserver.server.sendto(player.address,"ADD_CHAT:SERVER:PM:It's not your turn, you can't change a card's keywords right now!")
			else:
				self.gameserver.server.sendto(player.address,"ADD_CHAT:SERVER:PM:You can't change a card's keywords, the game hasn't started...")
			self.cleanup()
		else:
			return False
		return True

