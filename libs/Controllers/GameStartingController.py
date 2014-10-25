from Controller import*

from ..GUI.GUI import *
from ..netcom import Client
from ..Deck import MasterDeck, Card
from ..PickledCard import *

import string, os, thread, io, random

class GameStartingController(Controller):
	def init(self):
		#Clear the gui
		self.main.updated_elements = []
		self.main.main_element.clear()

		self.rerender = True
		self.last_rerendered = 0
		self.disable_framerate = True

		self.create_collage_surface()

		self.card_size = (int(0.7*200),200)
		self.card_img = pygame.Surface(self.card_size)
		self.current_message = "REQUESTING DECK"

		self.card_index = 0
		self.card_filename = ""
		self.cards_to_load = []
		self.main.master_deck = MasterDeck()

		self.start_time = float(self.main.time)

		self.main.client.send("REQUEST_DECK")

	def create_collage_surface(self):
		self.collage_surface = pygame.Surface(self.main.screen_size)
		self.collage_surface.fill((64,64,64))

	def check_current(self):
		#first we check if this card is in our defaults or customs
		card_name = self.cards_to_load[self.card_index]
		self.matching_card = None
		for card in self.main.my_master_deck.cards:
			if card.filename == card_name:
				self.matching_card = card
				break
		if self.matching_card != None:# we need to check if our card matches theirs
			self.main.client.send("REQUEST_CARDFILE_ATTRIBUTES:"+str(self.card_index))
		else:# we need to download the entire file
			self.main.client.send("REQUEST_CARDFILE:"+str(self.card_index))

	def check_next(self):
		self.card_index += 1
		if self.card_index >= len(self.cards_to_load):
			self.main.client.send("DONE_LOADING")
		else:
			self.check_current()

	def update(self):
		for e in self.main.events:
			if e.type == VIDEORESIZE:
				self.create_collage_surface()

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
			#print "RECEIVED CARD "+s2+"/"+str(len(self.cards_to_load))
			self.current_message = s2+"/"+str(len(self.cards_to_load))
			index = int(s2)
			s3 = s1[len(s2)+1:]
			#print s3[:1000]
			self.main.master_deck.unpickle_and_add_card(s3)
			print "'"+self.main.master_deck.cards[-1].name+"' downloaded."
			self.card_img = pygame.transform.smoothscale(self.main.master_deck.cards[-1].get_image(), self.card_size)
			self.add_to_collage()
			self.check_next()
		elif message.startswith("CARDFILE_ATTRIBUTES:"):
			self.rerender = True
			s1 = message[len("CARDFILE_ATTRIBUTES:"):]
			s2 = s1[:s1.index(":")]
			#print "RECEIVED CARD ATTRIBUTES "+s2+"/"+str(len(self.cards_to_load))
			self.current_message = s2+"/"+str(len(self.cards_to_load))
			index = int(s2)
			s3 = s1[len(s2)+1:]
			if self.matching_card.attributes != s3:
				#Our attributes file varies from theirs, so we have to download the entire card... poop.
				self.main.client.send("REQUEST_CARDFILE:"+str(self.card_index))
			else:
				self.main.master_deck.cards.append(self.matching_card)
				self.card_img = pygame.transform.smoothscale(self.main.master_deck.cards[-1].get_image(), self.card_size)
				self.add_to_collage()
				self.check_next()
		elif message == "CLIENT_READY":
			print "DURATION:",round(self.main.time - self.start_time,3)
			self.rerender = True
			self.main.play_sound("connected")
			import GameController
			self.main.controller = GameController.GameController(self.main)
		else:
			return False
		return True

	def add_to_collage(self):
		img1 = self.card_img.copy().convert()
		img1.fill((127,127,127), special_flags = BLEND_RGB_MULT)
		img2 = img1.copy()
		img1.set_colorkey((0,0,0))
		img2.set_colorkey((255,255,255))
		angle = random.randint(0,359)
		img1 = pygame.transform.rotate(img1, angle)
		img2 = pygame.transform.rotate(img2, angle)
		rect = img1.get_rect(center = (random.randint(0,self.main.screen_size[0]),
										   random.randint(0,self.main.screen_size[1])))
		self.collage_surface.blit(img1, rect, special_flags=BLEND_RGB_MAX)
		img2.set_alpha(127)
		self.collage_surface.blit(img2, rect)

	def render(self):
		if self.rerender or self.main.time-self.last_rerendered>1:
			self.last_rerendered = float(self.main.time)
			self.rerender = False
			self.main.screen.blit(self.collage_surface,(0,0))
			#self.main.screen.fill((127,127,127),special_flags = BLEND_RGB_MULT)
			text_img = self.main.font.render(self.current_message, True, (255,255,255))
			card_img = self.card_img
			card_rect = card_img.get_rect(center = (self.main.screen_size[0]/2, self.main.screen_size[1]/2))
			text_rect = text_img.get_rect(midbottom = card_rect.midtop)
			merged_rect = card_rect.union(text_rect)
			merged_rect.inflate_ip(10, 10)
			self.main.screen.fill((64,64,64), merged_rect, special_flags = BLEND_RGB_MULT)
			self.main.screen.blit(text_img,text_rect)
			self.main.screen.blit(card_img,card_rect)
