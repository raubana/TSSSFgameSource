import pygame
from pygame.locals import*
import os, random, math

from locals import *
from PickledCard import *
import Templatizer
from common import lerp, apply_shadow


def check_variable_name_is_legal(name):
	if name == "":
		raise SyntaxError("A variable can't be nameless")
	if name[0].isdigit():
		raise SyntaxError("A variable can't begin with a number.")
	for ch in name:
		if not ch.isalnum() and ch != "_":
			raise SyntaxError("A variable can't have the character '" + ch + "'")

def break_apart_line(line):
	parts = line.split("=")
	if len(parts) != 2:
		raise SyntaxError("Incorrect number of '='s in line '" + line + "'")
	variable = str(parts[0]).strip()
	value = str(parts[1]).strip()
	check_variable_name_is_legal(variable)
	return (variable, value)

def cut_and_paste_strip(src_img, dest_srf, p_rect, tint, shadow_color=(0,0,0)):
	size = dest_srf.get_size()
	rect = pygame.Rect(lerp(0,size[0],p_rect[0]),
					   lerp(0,size[1],p_rect[1]),
					   lerp(0,size[0],p_rect[2]),
					   lerp(0,size[1],p_rect[3]))
	srf = pygame.Surface(rect.size,SRCALPHA)
	srf.fill((255,255,255,0))
	srf.blit(src_img,(-rect.left,-rect.top))
	srf.fill(tint, None, special_flags = BLEND_RGB_MULT)
	pygame.draw.rect(srf, (255,255,255), (0,0,rect.width,rect.height), 7)
	srf = apply_shadow(srf,18,96,shadow_color)

	offset = 2
	p1 = (rect.left+lerp(-offset,offset,random.random()),rect.top+lerp(-offset,offset,random.random()))
	p2 = (rect.right+lerp(-offset,offset,random.random()),rect.bottom+lerp(-offset,offset,random.random()))
	center = ((p1[0]+p2[0])/2.0,(p1[1]+p2[1])/2.0)
	angle = math.degrees(math.atan2(rect.height,rect.width)-math.atan2(p2[1]-p1[1],p2[0]-p1[0]))
	new_srf = pygame.transform.rotozoom(srf, angle, 1.0)

	#new_srf = srf
	new_rect = new_srf.get_rect(center = center)#rect.center)
	dest_srf.blit(new_srf,new_rect)


class Deck(object):
	def __init__(self):
		self.cards = []

	def draw(self):
		if len(self.cards) == 0: return None
		return self.cards.pop(0)

	def add_card_to_top(self, card):
		self.cards.insert(0,card)

	def add_card_to_bottom(self, card):
		self.cards.append(card)

	def remove_card(self, card):
		if card in self.cards:
			self.cards.remove(card)
		else:
			raise LookupError("This card is not in this deck.")

	def shuffle(self):
		random.shuffle(self.cards)

	def get_transmit(self, master_deck):
		s = ""
		i = 0
		while i < len(self.cards):
			s += str(master_deck.cards.index(self.cards[i]))
			i += 1
			if i < len(self.cards):
				s +=","
		return s


class MasterDeck(object):
	def __init__(self):
		self.cards = []
		self.pc_cards = []

	def load_all_cards(self, pc_list=None, render=True):
		if pc_list == None:
			pc_list = []
			from CustomDeck import CustomDeck
			custom_deck = CustomDeck()
			custom_deck.follow_instructions("add_all")
			for f in custom_deck.list:
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
						print("loading '" + match + "'")
						pc = open_pickledcard(match)
						pc_list.append(pc)
		for pc in pc_list:
			print "parsing " + pc.filename
			pc_f = open(pc.filename, "rb")
			org_pc = pc_f.read()
			self.pc_cards.append(org_pc)
			pc_f.close()
			c = Card()
			c.parsePickledCard(pc, render)
			self.cards.append(c)

	def unpickle_and_add_card(self, s):
		self.pc_cards.append(s)
		pc = open_pickledcard(io.BytesIO(s))
		c = Card()
		c.parsePickledCard(pc)
		self.cards.append(c)


class Card(object):
	def __init__(self):
		self.original_image = pygame.Surface(CARD_SIZE, pygame.SRCALPHA)
		self.image = self.original_image.copy()
		self.name = None
		self.type = None
		self.gender = None
		self.race = None
		self.keywords = []
		self.power = None
		self.attributes = ""

		self.flagged_for_rerender = True

		self.printed_name = None
		self.printed_name_size = None

		self.temp_name = None
		self.temp_printed_name = None
		self.temp_printed_name_size = None
		self.temp_gender = None
		self.temp_race = None
		self.temp_keywords = None
		self.temp_to_be_discarded = False

		self.temp_image = None
		self.temp_card_being_imitated = None

		self.is_modified = False
		self.must_transmit_modifications = False

	def reset(self):
		self.set_temp_name(None,None,None)
		self.set_temp_gender(None)
		self.set_temp_race(None)
		self.set_temp_keywords(None)
		self.set_temp_image(None)
		self.set_temp_to_be_discarded(False)
		self.temp_card_being_imitated = None

		self.is_modified = False
		self.must_transmit_modifications = True

	def get_modified_transmit(self, master_deck):
		if self.is_modified:
			s = "MODIFIED_CARD:"
			#Any of these are left blank if they're 'None'.
			#CARD ID::Temp Name::Temp Printed Name::Temp Printed Name Size::Temp Gender::Temp Race::Temp Keywords::Temp To Be Discarded::Temp Card Being Imitated
			s += str(master_deck.cards.index(self)) + "::"
			L = [self.temp_name,self.temp_printed_name,self.temp_printed_name_size,self.temp_gender,self.temp_race,
				 self.temp_keywords,self.temp_to_be_discarded,self.temp_card_being_imitated]
			#print L
			i = 0
			while i < len(L):
				part = L[i]
				if part != None:
					t = type(part)
					if t in (str,unicode):
						s += part
					elif t in (bool,int):
						s += str(part)
					elif t in (list, tuple):
						s += string.join(part,",")
				i += 1
				if i < len(L):
					s += "::"
		else:
			s = "UNMODIFIED_CARD:"
			s += str(master_deck.cards.index(self))
		#print s
		return s

	def set_temp_name(self, name, printed_name, printed_name_size = None):
		if name != self.temp_name or printed_name != self.temp_printed_name or self.temp_printed_name_size != printed_name_size:
			if name == None:
				self.temp_name = None
			else:
				self.temp_name = str(name)
			if printed_name == None:
				self.temp_printed_name = None
			else:
				self.temp_printed_name = str(printed_name)
			if printed_name_size == None:
				self.temp_printed_name_size = None
			else:
				self.temp_printed_name_size = str(printed_name_size)
			self.flag_for_rerender()
			self.is_modified = True
			self.must_transmit_modifications = True

	def set_temp_gender(self, gender):
		if gender != self.temp_gender:
			self.temp_gender = gender
			self.flag_for_rerender()
			self.is_modified = True
			self.must_transmit_modifications = True

	def set_temp_race(self, race):
		if race != self.temp_race:
			self.temp_race = race
			self.flag_for_rerender()
			self.is_modified = True
			self.must_transmit_modifications = True

	def set_temp_keywords(self, keywords):
		if keywords != self.temp_keywords:
			self.temp_keywords = keywords
			self.flag_for_rerender()
			self.is_modified = True
			self.must_transmit_modifications = True

	def set_temp_image(self, image):
		if image != self.temp_image:
			self.temp_image = image
			self.flag_for_rerender()
			self.is_modified = True
			self.must_transmit_modifications = True

	def set_temp_to_be_discarded(self, discarded):
		if discarded != self.temp_to_be_discarded:
			self.temp_to_be_discarded = discarded
			self.flag_for_rerender()
			self.is_modified = True
			self.must_transmit_modifications = True

	def flag_for_rerender(self):
		self.flagged_for_rerender = True

	def imitate_card(self, card, master_deck):
		self.set_temp_name(card.name, card.printed_name, card.printed_name_size)
		self.set_temp_gender(str(card.gender))
		self.set_temp_race(str(card.race))
		self.set_temp_keywords(list(card.keywords))
		img = pygame.Surface((int((297/394.)*card.original_image.get_width()),
										  int((215/544.)*card.original_image.get_height())),
										 SRCALPHA)
		img.blit(card.original_image, (-int((63/394.)*card.original_image.get_width()),
										  -int((86/544.)*card.original_image.get_height())))
		self.set_temp_image(img)
		self.temp_card_being_imitated = master_deck.cards.index(card)

	def parsePickledCard(self, pc, render=True):
		#we need to parse each attribute individually in preparation for proper parsing.
		self.attributes = str(pc.attr)
		L = pc.attr.split("\n")
		attributes = {}
		for l in L:
			try:
				spl = break_apart_line(l)
				attributes[spl[0]] = spl[1]
			except:
				pass
		#now we get our type - this should be the very first attribute
		if len(attributes) == 0:
			raise EOFError("No attributes in card.")
		if "type" not in attributes:
			raise EOFError("No type in card.")
		elif attributes["type"] in ("pony", "ship", "goal"):
			self.type = attributes["type"]
		else:
			raise SyntaxError("Types are restricted to 'pony','ship', and 'goal'. Instead we got '" + attributes["type"] + "'")
		#TODO: Do individualized parsing of attributes for each type of card.
		if "name" in attributes:
			self.name = attributes["name"].replace("\\n"," ")
			self.printed_name = attributes["name"]
		if "name_font_size" in attributes:
			self.printed_name_size = attributes["name_font_size"]
		if "power" in attributes:
			self.power = attributes["power"]
		if "gender" in attributes:
			self.gender = attributes["gender"]
		if "race" in attributes:
			self.race = attributes["race"]
		if "keywords" in attributes:
			keywords = attributes["keywords"].split(",")
			self.keywords = []
			for keyword in keywords:
				self.keywords.append(keyword.strip())
		#THIS PART IS STRICTLY FOR TESTING PURPOSES
		if "temp_name" in attributes:
			self.temp_name = attributes["temp_name"]
		if "temp_printed_name" in attributes:
			self.temp_printed_name = attributes["temp_printed_name"]
		if "temp_printed_name_size" in attributes:
			self.temp_printed_name_size = attributes["temp_printed_name_size"]
		if "temp_gender" in attributes:
			self.temp_gender = attributes["temp_gender"]
		if "temp_race" in attributes:
			self.temp_race = attributes["temp_race"]
		if "temp_keywords" in attributes:
			keywords = attributes["temp_keywords"].split(",")
			self.temp_keywords = []
			for keyword in keywords:
				self.temp_keywords.append(keyword.strip())

		if render:
			#finally we need our image
			if "template" in attributes and attributes["template"] == "True":
				img = pygame.image.load(io.BytesIO(pc.img))#.convert_alpha()
				template = Templatizer.create_template_from_attributes(attributes, img)
				self.original_image = template.generate_image()
			else:
				self.original_image = pygame.image.load(io.BytesIO(pc.img))#.convert_alpha()
			if self.original_image.get_size() != CARD_SIZE:
				self.original_image = pygame.transform.smoothscale(self.original_image, CARD_SIZE)
		self.reset()
		self.flag_for_rerender()

	def rerender(self):
		if self.flagged_for_rerender:
			self.flagged_for_rerender = False
			self.image = self.original_image.copy()
			if self.temp_image != None or self.temp_keywords!=None or self.temp_race!=None or self.temp_gender!=None:
				#self.image.fill((220,220,220), None, special_flags = BLEND_RGB_MULT)
				#We draw out temporary changes.
				#We are going to create a template to help make this part faster.
				attr={}
				attr["template"] = "True"
				tint = (255,255,160)
				shadow_color = (0,0,0)
				if self.temp_card_being_imitated != None:
					attr["type"] = "pony"
				if self.temp_printed_name != None: attr["name"] = self.temp_printed_name
				if self.temp_printed_name_size != None: attr["name_font_size"] = self.temp_printed_name_size
				if self.temp_gender != None: attr["gender"] = self.temp_gender
				elif self.gender != None: attr["gender"] = self.gender
				if self.temp_race != None: attr["race"] = self.temp_race
				elif self.race != None: attr["race"] = self.race
				if self.temp_keywords != None: attr["keywords"] = string.join(self.temp_keywords,",")
				if self.temp_image != None:
					img = self.temp_image
				else:
					img = pygame.Surface((1,1))
					img.fill((255,255,255))
				template = Templatizer.create_template_from_attributes(attr,img)
				img = template.generate_image()
				if img.get_size() != CARD_SIZE:
					img = pygame.transform.smoothscale(img, CARD_SIZE)
				#Finally, we "cut strips" out of the template image and blit them onto the card's image.
				if self.temp_image != None:
					cut_and_paste_strip(img, self.image, (65/394.,85/544.,294/394.,216/544.), tint, shadow_color)
				if self.temp_printed_name != None:
					cut_and_paste_strip(img, self.image, (83/392.,15/542.,297/392.,75/542.), tint, shadow_color)
				if self.temp_keywords != None:
					cut_and_paste_strip(img, self.image, (47/392.,294/542.,325/392.,39/542.), tint, shadow_color)
				if self.temp_keywords != None and "DFP" in self.temp_keywords:
					cut_and_paste_strip(img, self.image, (23/392.,263/542.,64/392.,65/542.), tint, shadow_color)
				if self.temp_gender != None or self.temp_race != None:
					cut_and_paste_strip(img, self.image, (21/392.,18/542.,68/392.,122/542.), tint, shadow_color)

	def get_image(self):
		self.rerender()
		return self.image



