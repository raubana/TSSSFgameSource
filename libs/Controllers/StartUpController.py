from Controller import*

from ..GUI.GUI import *
from ..CustomDeck import *
from ..PickledCard import *
from ..Deck import*

import string, os, random

class StartUpController(Controller):
	def init(self):
		#Clear the gui
		self.main.updated_elements = []
		self.main.main_element.clear()
		self.main.main_element.set_text("")

		self.main.main_element.set_text("Loading...")

		if CLIENT_PRECACHE_DECK:
			self.custom_deck = CustomDeck()
			f = open("your_deck.txt")
			instructions = f.read()
			f.close()
			self.custom_deck.follow_instructions(instructions)

		self.disable_framerate = True

	def update(self):
			if CLIENT_PRECACHE_DECK and len(self.custom_deck.list) > 0:
				f = self.custom_deck.list.pop(0)
				if f.endswith(".tsssf") or f.endswith(".tsf"):
					match = None
					files = os.listdir("data/default_cards")
					if f in files:
						match = "data/default_cards/"+f
					else:
						files = os.listdir("cards")
						if f in files:
							match = "cards/"+f
					if match != None:
						print("loading and parsing '" + match + "'")
						pc = open_pickledcard(match)
						card = Card()
						card.parsePickledCard(pc, CLIENT_PRERENDER_DECK)
						card.filename = f
						self.main.my_master_deck.cards.append(card)
			else:
				import ConnectMenuController
				self.main.controller = ConnectMenuController.ConnectMenuController(self.main)
				self.main.controller.twilight_peak_start_time = float(self.main.time)
