import pygame
from GUI import *
from ..GUI.CardElement import *
from ..common import *


class TableElement(Element):
	def init(self):
		scale = 0.25
		grid_offset = 15
		self.card_size = (int(CARD_SIZE[0]*scale),int(CARD_SIZE[1]*scale))
		self.grid_size = (int(self.card_size[0]+grid_offset*2), int(self.card_size[1]+grid_offset*2))

	def do_nothing(self):
		pass

	def setup_grid(self):
		self.clear()

		#creates the grid
		for y in xrange(self.main.card_table.size[1]):
			for x in xrange(self.main.card_table.size[0]):
				works = False
				for Y in xrange(-1,2):
					for X in xrange(-1,2):
						index = (y+Y,x+X)
						if self.main.card_table.check_if_legal_index(index,"pony",self.main.master_deck.cards):
							works = True
							X = 3
							Y = 3
				if works:
					pos = (self.grid_size[0] * x, self.grid_size[1] * y)
					if (x)%2 == (y)%2:
						color = (198,185,224,255)
					else:
						color = (179,173,227,255)
					element = Element(self.main,self,pos,self.grid_size,bg=color)
					element.ignore_all_input = True

		#creates the pony cards
		for y in xrange(self.main.card_table.size[1]):
			for x in xrange(self.main.card_table.size[0]):
				card = self.main.card_table.pony_cards[y][x]
				if card != None:
					pos = 	(((self.grid_size[0] - self.card_size[0]) / 2) + self.grid_size[0] * x,
							  ((self.grid_size[1] - self.card_size[1]) / 2) + self.grid_size[1] * y)
					element = CardElement(self.main,self,pos,self.card_size)
					element.set_card(card)
					element.menu_info = [("Discard", self.do_nothing),
										 ("Action: Swap", self.do_nothing),
										 ("Action: Set Gender", self.do_nothing),
										 ("Action: Set Race", self.do_nothing),
										 ("Action: Give Keyword", self.do_nothing),
										 ("Action: Imitate Card", self.do_nothing)]

	def triggerMousePressed(self, mouse_pos, button):
		if button == 1:
			#we need to find which tile the player clicked into.
			#first we get out mouse_pos relative to the corner of the table element.
			if self.parent:
				corner = self.parent.get_world_pos()
			else:
				corner = (0,0)
			pos = [mouse_pos[0]-corner[0]-self.pos[0],mouse_pos[1]-corner[1]-self.pos[1]]
			#next we offset it by how much the table is offset on the x and y axes.
			if self.h_scrollbar != None:
				pos[0] = pos[0] + self.h_scrollbar.scrolled_amount
			if self.v_scrollbar != None:
				pos[1] = pos[1] + self.v_scrollbar.scrolled_amount
			#then we do some math to get our grid location.
			index = (floorint(pos[0]/self.grid_size[0]), floorint(pos[1]/self.grid_size[1]))
			#finally, we send this off to the server.
			self.main.client.send("CLICKED_GRID_AT:"+str(index[0])+","+str(index[1]))
