import pygame
from GUI import *
from ..GUI.CardElement import *
from ..common import *
from ..CardTable import xcoords_to_index


class TableElement(Element):
	def init(self):
		scale = 0.2
		grid_offset = 15
		self.card_size = (int(CARD_SIZE[0]*scale),int(CARD_SIZE[1]*scale))
		self.grid_size = (int(self.card_size[0]+grid_offset*2), int(self.card_size[1]+grid_offset*2))

		self.mouse_pos = None

	def do_nothing(self):
		pass

	def get_graphical_pos(self, index, card_type):
		if card_type == "pony":
			pos = 	(((self.grid_size[0] - self.card_size[0]) / 2) + self.grid_size[0] * index[0],
							  ((self.grid_size[1] - self.card_size[1]) / 2) + self.grid_size[1] * index[1])
		elif card_type == "h ship":
			pos = 	(((- self.card_size[1]) / 2) + self.grid_size[0] * (index[0]+1),
							  ((self.grid_size[1] - self.card_size[0]) / 2) + self.grid_size[1] * (index[1]+1))
		elif card_type == "v ship":
			pos = 	(((self.grid_size[0] - self.card_size[0]) / 2) + self.grid_size[0] * (index[0]+1),
							  ((-self.card_size[1]) / 2) + self.grid_size[1] * (index[1]+1))
		return pos

	def setup_grid(self):
		old_elements = {}

		i = len(self.children) - 1
		while i >= 0:
			child = self.children[i]
			if type(child) == CardElement:
				old_elements[child.card.name] = child
				self._remove_child(child)
			i -= 1

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
					pos = self.get_graphical_pos((x,y), "v ship")
					if card.name in old_elements and old_elements[card.name].angle == 0:
						element = old_elements[card.name]
						del old_elements[card.name]
						self._add_child(element)
						element.set_pos(pos)
					else:
						element = CardElement(self.main,self,pos,self.card_size)
						element.set_card(card, 127)
						element.menu_info = [("Discard", self.do_nothing)]

		#creates the h ship cards
		for y in xrange(self.main.card_table.size[1]):
			for x in xrange(self.main.card_table.size[0]-1):
				card = self.main.card_table.h_ship_cards[y][x]
				if card != None:
					pos = self.get_graphical_pos((x,y), "h ship")
					if card.name in old_elements and old_elements[card.name].angle == 90:
						element = old_elements[card.name]
						del old_elements[card.name]
						self._add_child(element)
						element.set_pos(pos)
					else:
						element = CardElement(self.main,self,pos,[self.card_size[1],self.card_size[0]])
						element.set_card(card, 127, 90)
						element.menu_info = [("Discard", self.do_nothing)]

		#creates the pony cards
		for y in xrange(self.main.card_table.size[1]):
			for x in xrange(self.main.card_table.size[0]):
				card = self.main.card_table.pony_cards[y][x]
				if card != None:
					pos = self.get_graphical_pos((x,y), "pony")
					if card.name in old_elements:
						element = old_elements[card.name]
						del old_elements[card.name]
						self._add_child(element)
						element.set_pos(pos)
					else:
						element = CardElement(self.main,self,pos,self.card_size)
						element.set_card(card)
						element.menu_info = [("Discard", self.do_nothing),
											 ("Action: Swap", self.do_nothing),
											 ("Action: Set Gender", self.do_nothing),
											 ("Action: Set Race", self.do_nothing),
											 ("Action: Give Keyword", self.do_nothing),
											 ("Action: Imitate Card", self.do_nothing)]

		#we dispose of the remaining old_elements
		for key in old_elements:
			del old_elements[key]

	def mousepos_to_xcoords(self, mouse_pos):
		index = (floorint(mouse_pos[0]/self.grid_size[0]), floorint(mouse_pos[1]/self.grid_size[1]))

		center = ((index[0]+0.5)*self.grid_size[0], (index[1]+0.5)*self.grid_size[1])
		offset = ((mouse_pos[0]-center[0])/float(self.grid_size[0]),(mouse_pos[1]-center[1])/float(self.grid_size[1]))
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

		return index

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

			index = self.mousepos_to_xcoords(pos)

			#finally, we send this off to the server.
			self.main.client.send("CLICKED_GRID_AT:"+str(index[0])+","+str(index[1]))

	def triggerMouseMove(self, mouse_pos):
		if self.hover:
			if self.parent:
				corner = self.parent.get_world_pos()
			else:
				corner = (0,0)
			self.mouse_pos = [mouse_pos[0]-corner[0]-self.pos[0],mouse_pos[1]-corner[1]-self.pos[1]]
			self.flag_for_rerender()
		else:
			if self.mouse_pos != None:
				self.flag_for_rerender()
				self.mouse_pos = None

	def rerender_foreground(self):
		if self.mouse_pos != None:
			offset = [0,0]
			if self.h_scrollbar != None:
				offset[0] = self.h_scrollbar.scrolled_amount
			if self.v_scrollbar != None:
				offset[1] = self.v_scrollbar.scrolled_amount
			mouse_pos = (self.mouse_pos[0]+offset[0], self.mouse_pos[1]+offset[1])
			xcoords = self.mousepos_to_xcoords(mouse_pos)

			#draw h ship
			info = xcoords_to_index(xcoords, "ship")
			index = info[1]
			if info[0] == "h ship":
				pos = self.get_graphical_pos(index, "h ship")
				pygame.draw.rect(self.rendered_surface, (255,0,255), (pos[0]-offset[0],pos[1]-offset[1],self.card_size[1],self.card_size[0]), 2)
			elif info[0] == "v ship":
				pos = self.get_graphical_pos(index, "v ship")
				pygame.draw.rect(self.rendered_surface, (255,0,255), (pos[0]-offset[0],pos[1]-offset[1],self.card_size[0],self.card_size[1]), 2)

			#draw pony
			info = xcoords_to_index(xcoords, "pony")
			index = info[1]
			if info[0] == "pony":
				pos = self.get_graphical_pos(index, "pony")
				pygame.draw.rect(self.rendered_surface, (127,0,255), (pos[0]-offset[0],pos[1]-offset[1],self.card_size[0],self.card_size[1]), 2)
