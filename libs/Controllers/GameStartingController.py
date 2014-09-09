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
		self.current_message = "REQUESTING DECK SIZE"

		self.number_of_cards = None
		self.main.master_deck = MasterDeck()

		self.main.client.send("REQUEST_DECKSIZE")

	def read_message(self, message):
		if message.startswith("DECKSIZE:"):
			self.rerender = True
			self.number_of_cards = int(message[len("DECKSIZE:"):])
			if self.number_of_cards > 0:
				self.main.client.send("REQUEST_CARDFILE:0")
			else:
				print "EMPTY DECK!!"
				self.main.client.close()
		elif message.startswith("CARDFILE:"):
			self.rerender = True
			s1 = message[len("CARDFILE:"):]
			s2 = s1[:s1.index(":")]
			print "RECEIVED CARD "+s2+"/"+str(self.number_of_cards)
			self.current_message = s2+"/"+str(self.number_of_cards)
			index = int(s2)
			s3 = s1[len(s2)+1:]
			#print s3[:1000]
			self.main.master_deck.unpickle_and_add_card(s3)
			self.card_img = pygame.transform.smoothscale(self.main.master_deck.cards[-1].image, self.card_size)
			if len(self.main.master_deck.cards) == self.number_of_cards:
				self.main.client.send("DONE_LOADING")
				self.current_message = "Done loading!"
			else:
				self.main.client.send("REQUEST_CARDFILE:"+str(len(self.main.master_deck.cards)))
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
