import pygame
from pygame.locals import *

pygame.init()

import time, string

from libs.GUI.GUI import *
from libs.common import *
from libs.Templatizer import *


class Main(object):
	def __init__(self):
		self.screen_size = (800,600)
		self.screen = pygame.display.set_mode(self.screen_size, RESIZABLE)

		# SETS UP THE GUI
		self.element_level = 0

		self.updated_elements = []
		self.elements_to_pack = {}

		self.needs_to_pack = False
		self.focus = None
		self.tooltip_text = None
		self.hover_focus_time = 0
		self.tooltip_surface = None

		self.font = None

		self.main_element = Element(self, self, (0,0), self.screen_size, bg=(210,180,220))
		self.main_element.set_text_align(ALIGN_MIDDLE)

		self.manage_pack_requests()

		self.reset()
		self.run()

	def reset(self):
		"""
		"""
		# ========== PONIES ==========
		"""
		self.template = Templatizer(	CARDBACK_START,
					   					pygame.image.load("imgs/temp_card_img.png"),
					   					"Fanfic Author Twilight",
					   					["Mane 6","Twilight Sparkle"],
					   					"Place this card in the center of the table at the start of the game.\nThis card cannot be moved or removed from the grid. This power can't be copied.",
					   					"She was no writer. She was a prophet. Her words spanned the universes, sang hymns to the terrible improbability of life and love. She was like unto a god, Twilight was.\n- Element of Magic: An Autobiography",
					   					"Core 1.0.3 Copyright 2014 Horrible People Games. Art by Pixel Prism.",
										[SPRITE_FEMALE,SPRITE_UNICORN])
		self.original_img = pygame.image.load("imgs/split pages/pony/1_1_1.png")
		"""
		"""
		self.template = Templatizer(	CARDBACK_PONY,
					   					pygame.image.load("imgs/temp_card_img.png"),
					   					"Private Eye Twilight",
					   					["Mane 6","Twilight Sparkle"],
					   					"Pound the Pavement (Swap): You may swap 2 Pony cards on the shipping grid. Neither of their powers activate.",
					   					"The rain ran its soggy fingers down the icy window panes. I listened to the ice crackle in my glass, pondering what I'd done in a past life to put me into this hell hole. Three dead partners, two bullet wounds, and one long therapy bill later, and here I am. But, as they say in this city, \"You gotta pay the bills.\" - Casaflanka",
					   					"Core 1.0.3 Copyright 2014 Horrible People Games. Art by Pixel Prism.",
										[SPRITE_FEMALE,SPRITE_UNICORN])
		self.original_img = pygame.image.load("imgs/split pages/pony/1_1_2.png")
		"""
		"""
		self.template = Templatizer(	CARDBACK_PONY,
					   					pygame.image.load("imgs/temp_card_img.png"),
					   					"Applejack: the Cutest, Smartest, All-Around-Best Background Pony",
					   					["Apple","Applejack","Mane 6"],
					   					"Another Derpy Episode (Swap): You may swap 2 Pony cards on the shipping grid. Neither of their powers activate.",
					   					"The day was saved again, by Twilight and all her best friends: Fluttershy, Rainbow Dash, Pinkie Pie, and Rarity!\n - The Gang's All Here",
					   					"Core 1.0.3 Copyright 2014 Horrible People Games. Art by Pixel Prism.",
										[SPRITE_FEMALE,SPRITE_EARTH],
										title_font_size=43)
		self.original_img = pygame.image.load("imgs/split pages/pony/3_1_1.png")
		"""

		self.template = Templatizer(	CARDBACK_PONY,
					   					pygame.image.load("imgs/temp_card_img.png"),
					   					"Freedom Fighter\nPinkie Pie",
					   					["Mane 6","Pinkie Pie"],
					   					"Revolution! (Special): You may search the Ship and/or Pony discard piles for up to 2 cards of your choice and put them into your hand. If any of those cards are still in your hand at the end of your turn, discard them.",
					   					"\"I see you there, Empress! Can you hear it? Can you hear the ponies singing for the revolution? Singing for your DOOM?!\"\n- Of Ponies and Peril, Chapter 34",
					   					"Core 1.0.3 Copyright 2014 Horrible People Games. Art by Pixel Prism.",
										[SPRITE_FEMALE, SPRITE_EARTH, SPRITE_DFP],
										power_font_size=35)
		self.original_img = pygame.image.load("imgs/split pages/pony/2_1_3.png")

		"""
		self.template = Templatizer(	CARDBACK_PONY,
					   					pygame.image.load("imgs/temp_card_img.png"),
					   					"Changeling",
					   					["Changeling","Villain"],
					   					"Gains the name, keywords, and symbols of any single 9 of your choice until end of turn. If this card is moved to a new place on the grid, the current player must select a new disquise that will last until the end of their turn, even if other cards say its power would not activate.",
					   					"C'karr flung his perforated hooves around Twilight, his veil dropping. \"Do you think a little thing like that can stop true friendship?\" - The Thatched Roof Hive",
					   					"Core 1.0.3 Copyright 2014 Horrible People Games. Art by Pixel Prism.",
										[SPRITE_CHANGELING_PEGASUS],
										power_font_size=35)
		self.original_img = pygame.image.load("imgs/split pages/pony/6_1_3.png")
		"""
		# ========== SHIP ==========
		"""
		self.template = Templatizer(	CARDBACK_SHIP,
					   					pygame.image.load("imgs/temp_card_img.png"),
					   					"So THAT'S What That Does!",
					   					["Race Change"],
					   					"When you attach this card to the grid, you may choose one Pony card attached to this Ship. Until the end of your turn, that Pony card counts as a race of your choice. This cannot affect Changelings.",
					   					"Serendipity, that's what it was. \"Mistake\" is such an ugly word... - Magical Makeover",
					   					"Core 1.0.3 Copyright 2014 Horrible People Games. Art by Pixel Prism.",
										[SPRITE_SHIP])
		self.original_img = pygame.image.load("imgs/split pages/ship/8_1_2.png")
		"""
		"""
		self.template = Templatizer(	CARDBACK_SHIP,
					   					pygame.image.load("imgs/temp_card_img.png"),
					   					"Do You Think Love Can Bloom? Even On a Battlefield?",
					   					["Timeline Change"],
					   					"When you attach this card to the grid, you may choose one Pony card attached to this Ship. Until the end of your turn, that Pony card connected with this Ship counts as $.",
					   					"Twilight just stared blankly into her codec at Spike. She was doing that a lot lately. - Of Ponies and Peril, Chapter 22",
					   					"Core 1.0.3 Copyright 2014 Horrible People Games. Art by Pixel Prism.",
										[SPRITE_SHIP],
										title_font_size=43)
		self.original_img = pygame.image.load("imgs/split pages/ship/9_1_1.png")
		"""
		# ========== GOAL ==========
		"""
		self.template = Templatizer(	CARDBACK_GOAL,
					   					pygame.image.load("imgs/temp_card_img.png"),
					   					"Rainbow Dash Fan Club",
					   					[],
					   					"Win this Goal when:\n2 Rainbow Dashes are shipped together.",
					   					"\"I bet I could beat you at wrestling!\" shouted Rainbow Dash. The other Rainbow Dash pounced, wings flared. \"You're on!!\"\n-Rock and Roll All Night",
					   					"Core 1.0.3 Copyright 2014 Horrible People Games. Art by Pixel Prism.",
										[SPRITE_GOAL,SPRITE_2])
		self.original_img = pygame.image.load("imgs/split pages/goal/14_1_3.png")
		"""
		"""
		self.template = Templatizer(	CARDBACK_GOAL,
					   					pygame.image.load("imgs/temp_card_img.png"),
					   					"Shining Armor Approves\nof This Experiment!",
					   					[],
					   					"Win this Goal when:\nCadance is shipped with any *.",
					   					"Shining Armor smiled at Cadance tenderly. \"I promise I won't get mad. You should explore what you need to explore.\" Inside, he was buzzing with excitement!\n- Secret Pictures",
					   					"Core 1.0.3 Copyright 2014 Horrible People Games. Art by Pixel Prism.",
										[SPRITE_GOAL,SPRITE_1])
		self.original_img = pygame.image.load("imgs/split pages/goal/15_2_2.png")
		"""
		"""
		self.template = Templatizer(	CARDBACK_GOAL,
					   					pygame.image.load("imgs/temp_card_img.png"),
					   					"Help! I'm Trapped in a Shipping Card Game!",
					   					[],
					   					"Win this Goal when:\nCheerilee is shipped with anypony.\nAnypony at all.\nThe player who completes this Goal increases their hand size by 1 for the rest of the game.",
					   					"What are you doing? Put down the card and get me out of here! HELP!!! - Unknown",
					   					"Core 1.0.3 Copyright 2014 Horrible People Games. Art by Pixel Prism.",
										[SPRITE_GOAL,SPRITE_0],
										power_font_size=35)
		self.original_img = pygame.image.load("imgs/split pages/goal/16_1_2.png")
		"""

		self.template_img = self.template.generate_image()
		#pygame.image.save(self.template_img, "example.png")

		self.main_element.clear()
		self.main_element.h_scrollable = True
		self.main_element.v_scrollable = True

		self.image = Element(self, self.main_element, preferred_size=(788,1088), bg=ScaleImage(self.template_img))

		self.start_time = time.time()

	def _setup_for_pack(self):
		# THIS SHOULD NOT BE CALLED UNLESS YOU KNOW WHAT YOU'RE DOING!!
		if self.needs_to_pack == False:
			self.needs_to_pack = True
			level_name = str(self.element_level)
			if level_name not in self.elements_to_pack:
				level = []
				self.elements_to_pack[level_name] = level
			else:
				level = self.elements_to_pack[level_name]
			level.append(self)

	def manage_pack_requests(self):
		# managed elements needing to be packed
		while len(self.elements_to_pack) > 0:
			#first we find the highest level needed to be packed
			keys = self.elements_to_pack.keys()
			highest = int(keys[0])
			for key in keys[1:]:
				highest = min(highest, int(key))
			#next, we make each element in that level pack
			elements_to_pack = self.elements_to_pack.pop(str(highest))
			for element in elements_to_pack:
				element.pack()

	def update(self):
		for e in self.events:
			if e.type == MOUSEMOTION:
				self.mouse_pos = e.pos
				self.main_element.update_for_mouse_move(e.pos)
			elif e.type == MOUSEBUTTONDOWN:
				if DEBUG_MOUSEBUTTONPRESS_TRACE:
					print ""
				if e.button <= 3: self.mouse_button[e.button-1] = True
				self.main_element.update_for_mouse_button_press(e.pos, e.button)
			elif e.type == MOUSEBUTTONUP:
				if e.button <= 3: self.mouse_button[e.button-1] = False
				self.main_element.update_for_mouse_button_release(e.pos, e.button)

			elif e.type == KEYDOWN:
				self.keys[e.key] = True
				if self.focus != None:
					self.focus.update_for_keydown(e.unicode, e.key)
			elif e.type == KEYUP:
				self.keys[e.key] = False
				if self.focus != None:
					self.focus.update_for_keyup(e.key)

			elif e.type == VIDEORESIZE:
				self.screen_size = e.size
				self.screen = pygame.display.set_mode(self.screen_size, RESIZABLE)
				self.main_element.flag_for_rerender()
				self.main_element.flag_for_pack()

		toggle = (self.time - self.start_time)%1.0 >= 0.5
		if toggle and self.image.bg != self.template_img:
			self.image.set_bg(ScaleImage(self.template_img))
		elif not toggle and self.image.bg != self.original_img:
			self.image.set_bg(ScaleImage(self.original_img))

		for element in self.updated_elements:
			element.update()

	def set_tooltip_text(self, text):
		if text != self.tooltip_text:
			if type(text) in (str,unicode):
				self.tooltip_text = str(text)
			else:
				self.tooltip_text = None
			self.hover_focus_time = float(self.time)
			self.tooltip_surface = None
			self.main_element.flag_for_rerender()

	def move(self):
		pass

	def pack(self):
		if self.needs_to_pack:
			self.needs_to_pack = False

			new_pos = (0,0)
			new_size = self.screen_size
			redo = False
			if new_pos != self.main_element.pos:
				redo = True
				self.main_element.pos = new_pos
			if new_size != self.main_element.size:
				redo = True
				self.main_element.size = new_size
				self.main_element._setup_for_pack()
			if redo:
				self.main_element.update_rect()
				self.main_element.flag_for_rerender()

	def render(self):
		#Main Element (the GUI)
		self.main_element.render()

		pygame.display.flip()

	def run(self):
		self.running = True
		while self.running:
			self.time = time.time()
			self.keys = list(pygame.key.get_pressed())
			self.mouse_pos = list(pygame.mouse.get_pos())
			self.mouse_button = list(pygame.mouse.get_pressed())
			self.events = pygame.event.get()

			self.update()
			self.manage_pack_requests()
			self.move()
			self.manage_pack_requests()
			self.render()

			for e in self.events:
				if e.type == QUIT:
					print "Normal quit."
					self.running = False

		print "GOODBYE!!"
		pygame.quit()


main = Main()