from Controller import*

from ..GUI.GUI import *
from ..netcom import Client
from ..Deck import MasterDeck, Card
from ..PickledCard import *

import string, os, thread, io

class GameStartingController(Controller):
	def init(self):
		#Clear the gui
		self.main.updated_elements = []
		self.main.main_element.clear()

		self.rerender = True
		self.last_rerendered = 0

		self.card_size = (int(0.7*200),200)
		self.card_img = pygame.Surface(self.card_size)
		self.current_message = "REQUESTING DECK"

		self.card_index = 0
		self.card_filename = ""
		self.cards_to_load = []
		self.main.master_deck = MasterDeck()

		self.main.client.send("REQUEST_DECK")

	def check_current(self):
		#first we check if this card is in our defaults or customs
		card_name = self.cards_to_load[self.card_index]
		match = None
		if os.path.isfile("data/default_cards/"+card_name):
			match = "data/default_cards/"+card_name
		elif os.path.isfile("cards/"+card_name):
			match = "cards/"+card_name
		if match:# we need to check if our card matches theirs
			self.card_filename = match
			self.main.client.send("REQUEST_CARDFILE_ATTRIBUTES:"+str(self.card_index))
		else:# we need to download the entire file
			self.main.client.send("REQUEST_CARDFILE:"+str(self.card_index))

	def check_next(self):
		self.card_index += 1
		if self.card_index >= len(self.cards_to_load):
			self.main.client.send("DONE_LOADING")
		else:
			self.check_current()

	def read_message(self, message):
		if message.startswith("DECK:"):
			self.rerender = True
			self.cards_to_load = message[len("DECK:"):].split(",")
			if len(self.cards_to_load) > 0:
				self.check_current()
			else:
				print "EMPTY DECK!!"
				self.main.client.close()
		elif message.startswith("CARDFILE:"):
			self.rerender = True
			s1 = message[len("CARDFILE:"):]
			s2 = s1[:s1.index(":")]
			print "RECEIVED CARD "+s2+"/"+str(len(self.cards_to_load))
			self.current_message = s2+"/"+str(len(self.cards_to_load))
			index = int(s2)
			s3 = s1[len(s2)+1:]
			#print s3[:1000]
			self.main.master_deck.unpickle_and_add_card(s3)
			self.card_img = pygame.transform.smoothscale(self.main.master_deck.cards[-1].image, self.card_size)
			self.check_next()
		elif message.startswith("CARDFILE_ATTRIBUTES:"):
			self.rerender = True
			s1 = message[len("CARDFILE_ATTRIBUTES:"):]
			s2 = s1[:s1.index(":")]
			print "RECEIVED CARD ATTRIBUTES "+s2+"/"+str(len(self.cards_to_load))
			self.current_message = s2+"/"+str(len(self.cards_to_load))
			index = int(s2)
			s3 = s1[len(s2)+1:]
			pc_card = open_pickledcard(self.card_filename)
			if pc_card.attr != s3:
				#Our attributes file varies from theirs, so we have to download the entire card... poop.
				self.main.client.send("REQUEST_CARDFILE:"+str(self.card_index))
			else:
				card = Card()
				card.parsePickledCard(pc_card)
				self.main.master_deck.cards.append(card)
				self.card_img = pygame.transform.smoothscale(self.main.master_deck.cards[-1].image, self.card_size)
				self.check_next()
		elif message == "CLIENT_READY":
			self.rerender = True
			self.main.play_sound("connected")
			import GameController
			self.main.controller = GameController.GameController(self.main)
		else:
			return False
		return True

	def render(self):
		if self.rerender or self.main.time-self.last_rerendered>1:
			self.last_rerendered = float(self.main.time)
			self.rerender = False
			self.main.screen.fill((0,0,0))
			text_img = self.main.font.render(self.current_message, True, (255,255,255))
			card_img = self.card_img
			card_rect = card_img.get_rect(center = (self.main.screen_size[0]/2, self.main.screen_size[1]/2))
			text_rect = text_img.get_rect(midbottom = card_rect.midtop)
			self.main.screen.blit(text_img,text_rect)
			self.main.screen.blit(card_img,card_rect)
