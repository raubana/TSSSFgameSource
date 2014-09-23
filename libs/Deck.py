import pygame
import os, random

from locals import *
from PickledCard import *


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

	def load_all_cards(self, pc_list=None):
		if pc_list == None:
			pc_list = []
			files = os.listdir("cards")
			for f in files:
				if f.endswith(".tsssf") or f.endswith(".tsf"):
					print("loading '" + f + "'")
					pc = open_pickledcard("data/default_cards/" + f)
					pc_list.append(pc)
		for pc in pc_list:
			print "parsing " + pc.filename
			pc_f = open(pc.filename, "rb")
			org_pc = pc_f.read()
			self.pc_cards.append(org_pc)
			pc_f.close()
			c = Card()
			c.parsePickledCard(pc)
			self.cards.append(c)

	def unpickle_and_add_card(self, s):
		self.pc_cards.append(s)
		pc = open_pickledcard(io.BytesIO(s))
		c = Card()
		c.parsePickledCard(pc)
		self.cards.append(c)


class Card(object):
	def __init__(self):
		self.image = pygame.Surface(CARDSIZE, pygame.SRCALPHA)
		self.name = None
		self.type = None
		self.attributes = ""

	def parsePickledCard(self, pc):
		# first we need our image
		self.image = pygame.image.load(io.BytesIO(pc.img))#.convert_alpha()
		#next we need to parse each attribute individually in preparation for proper parsing.
		self.attributes = str(pc.attr)
		attributes = pc.attr.split("\n")
		i = 0
		while i < len(attributes):
			attributes[i] = break_apart_line(str(attributes[i]))
			i += 1
		#now we get our type - this should be the very first attribute
		if len(attributes) == 0:
			raise EOFError("No attributes in card.")
		first = attributes[0]
		if first[0] != "type":
			raise SyntaxError("First line of attributes should be for variable 'type'.")
		if first[1] in ("pony", "ship", "goal"):
			self.type = first[1]
		else:
			raise SyntaxError("Types are restricted to 'pony','ship', and 'goal'. Instead we got '" + first[1] + "'")
		#TODO: Do individualized parsing of attributes for each type of card.
		for attr in attributes[1:]:
			if attr[0] == "name":
				self.name = attr[1]
