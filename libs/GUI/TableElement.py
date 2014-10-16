import pygame
from GUI import *
from ..GUI.CardElement import *
from ..common import *


class TableElement(Element):
	def init(self):
		scale = 0.2
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
				if self.main.card_table.check_if_legal_index((x,y),"pony",self.main.master_deck.cards):
					for offset in ((0,0),(-1,0),(0,-1),(1,0),(0,1)):
						index = (x+offset[0],y+offset[1])
						if self.main.card_table.check_if_legal_index(index,"pony",self.main.master_deck.cards):
							if not self.main.card_table.check_if_legal_index(index,"pony"):
								works = True
								break
					if works:
						pos = (self.grid_size[0] * x, self.grid_size[1] * y)
						if (x)%2 == (y)%2:
							color = (198,185,224,255)
						else:
							color = (179,173,227,255)
						element = Element(self.main,self,pos,self.grid_size,bg=color)
						element.ignore_all_input = True

		#creates the v ship cards
		for y in xrange(self.main.card_table.size[1]-1):
			for x in xrange(self.main.card_table.size[0]):
				card = self.main.card_table.v_ship_cards[y][x]
				if card != None:
					pos = 	(((self.grid_size[0] - self.card_size[0]) / 2) + self.grid_size[0] * (x+1),
							  ((-self.card_size[1]) / 2) + self.grid_size[1] * (y+1))
					element = CardElement(self.main,self,pos,self.card_size)
					element.set_card(card, 127)
					element.menu_info = [("Discard", self.do_nothing)]

		#creates the h ship cards
		for y in xrange(self.main.card_table.size[1]):
			for x in xrange(self.main.card_table.size[0]-1):
				card = self.main.card_table.h_ship_cards[y][x]
				if card != None:
					pos = 	(((- self.card_size[0]) / 2) + self.grid_size[0] * (x+1),
							  ((self.grid_size[1] - self.card_size[1]) / 2) + self.grid_size[1] * (y+1))
					element = CardElement(self.main,self,pos,self.card_size)
					element.set_card(card, 127)
					element.menu_info = [("Discard", self.do_nothing)]

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

			#BUT WAIT; THERE'S MORE!
			#We have to compare this grid's center with the mouse position to get our "special" grid position.
			#("Special" meaning it can be used to describe both pony and ship card positions).

			center = ((index[0]+0.5)*self.grid_size[0], (index[1]+0.5)*self.grid_size[1])
			offset = ((pos[0]-center[0])/float(self.grid_size[0]),(pos[1]-center[1])/float(self.grid_size[1]))
			if abs(offset[0]) > abs(offset[1]):
				if offset[0] >= 0:
					index = (index[0]*3+2 , index[1]*3+1 )
				else:
					index = (index[0]*3+0 , index[1]*3+1 )
			else:
				if offset[1] >= 0:
					index = (index[0]*3+1 , index[1]*3+2 )
				else:
					index = (index[0]*3+1 , index[1]*3+0 )

			#finally, we send this off to the server.
			self.main.client.send("CLICKED_GRID_AT:"+str(index[0])+","+str(index[1]))
