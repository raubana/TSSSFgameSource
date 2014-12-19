import pygame
from GUI import *
from ..GUI.CardElement import *
from ..common import *
from ..CardTable import xcoords_to_index, CardTable


class TableElement(Element):
	def init(self):
		self.main.updated_elements.append(self)

		self.mouse_pos = None
		self.old_mouse_pos = None
		self.total_offset = [0,0]
		self.total_scroll = [0,0]
		self.total_size = [0,0]

		self.zoom = None

		self.min_zoom = 0.1
		self.max_zoom = 0.6
		self.zoom_ticks = 5
		self.set_zoom(0)

		self.being_dragged = False
		self.start_drag = False

		self.element_table = CardTable()

	def do_nothing(self):
		pass
	def discard_card(self, args):
		self.main.client.send("DISCARD_CARD:"+str(args[0]))
	def swap_card(self, args):
		self.main.client.send("SWAP_CARD:"+str(args[0]))
	def swap_gender(self, args):
		self.main.client.send("SWAP_GENDER:"+str(args[0]))
	def move_card(self, args):
		self.main.client.send("MOVE_CARD:"+str(args[0]))
	def imitate_card(self, args):
		self.main.client.send("IMITATE_CARD:"+str(args[0]))
	def change_race(self, args):
		self.main.client.send("CHANGE_RACE:"+str(args[0])+","+args[1])
	def make_princess(self, args):
		self.main.client.send("ADD_KEYWORD:"+str(args[0])+",Princess")
	def make_dfp(self, args):
		self.main.client.send("ADD_KEYWORD:"+str(args[0])+",DFP")

	def get_graphical_pos(self, index, card_type):
		if card_type == "pony":
			pos = 	(((self.tile_size[0] - self.card_size[0]) / 2) + self.tile_size[0] * index[0],
							  ((self.tile_size[1] - self.card_size[1]) / 2) + self.tile_size[1] * index[1])
		elif card_type == "h ship":
			pos = 	(((- self.card_size[1]) / 2) + self.tile_size[0] * (index[0]+1),
							  ((self.tile_size[1] - self.card_size[0]) / 2) + self.tile_size[1] * (index[1]+1))
		elif card_type == "v ship":
			pos = 	(((self.tile_size[0] - self.card_size[0]) / 2) + self.tile_size[0] * (index[0]+1),
							  ((-self.card_size[1]) / 2) + self.tile_size[1] * (index[1]+1))
		pos = (pos[0]+self.total_scroll[0], pos[1]+self.total_scroll[1])
		return pos

	def set_scroll(self, new_scroll):
		new_scroll = (int(new_scroll[0]),int(new_scroll[1]))
		if new_scroll != self.total_scroll:
			self.total_scroll = new_scroll
			#self.setup_grid()
			self.realign_children()
			self.flag_for_rerender()

	def triggerMousePressed(self, mouse_pos, button):
		if button == 1 and not self.being_dragged:
			world_pos = self.get_world_pos()
			pos = (mouse_pos[0] - world_pos[0] - self.total_scroll[0], mouse_pos[1] - world_pos[1] - self.total_scroll[1])
			index = self.mousepos_to_xcoords(pos)

			#finally, we send this off to the server.
			self.main.client.send("CLICKED_GRID_AT:"+str(index[0])+","+str(index[1]))
		elif button == 3:
			self.start_drag = True
		elif button in (4, 5):
			world_pos = self.get_world_pos()
			pos = (mouse_pos[0] - world_pos[0] - self.total_scroll[0], mouse_pos[1] - world_pos[1] - self.total_scroll[1])
			if button == 4:
				self.zoom_in(pos)
			else:
				self.zoom_out(pos)
			self.triggerMouseMove(mouse_pos)

	def triggerMouseMove(self, mouse_pos):
		if self.hover:
			world_pos = self.get_world_pos()
			self.mouse_pos = (mouse_pos[0] - world_pos[0] - self.total_scroll[0], mouse_pos[1] - world_pos[1] - self.total_scroll[1])
			self.flag_for_rerender()
		else:
			if self.mouse_pos != None:
				self.flag_for_rerender()
				self.mouse_pos = None

	def handle_event_mousepress(self, widget, mouse_pos_local, button):
		if button in (4, 5):
			self.triggerMousePressed(mouse_pos_local, button)

	def zoom_in(self, center=None):
		new_zoom = self.current_zoom_tick + 1
		self.set_zoom(new_zoom, center)

	def zoom_out(self, center=None):
		new_zoom = self.current_zoom_tick - 1
		self.set_zoom(new_zoom, center)

	def set_zoom(self, new_zoom, center=None, force=False):
		if center == None:
			center = (0, 0)

		new_zoom = min(max(new_zoom, 0), self.zoom_ticks)
		self.current_zoom_tick = new_zoom
		new_zoom = lerp(self.min_zoom,self.max_zoom,(new_zoom/float(self.zoom_ticks))**2 )

		if new_zoom != self.zoom or force:
			if self.zoom != None:
				original_zoom = float(self.zoom)
			else:
				original_zoom = None

			self.zoom = new_zoom
			self.card_size = (int(CARD_SIZE[0] * self.zoom), int(CARD_SIZE[1] * self.zoom))
			gap = min(CARD_SIZE)* self.zoom * 0.25
			self.tile_size = (int(CARD_SIZE[0] * self.zoom + gap), int(CARD_SIZE[1] * self.zoom + gap))

			self.total_size = (self.tile_size[0] * self.main.card_table.size[0], self.tile_size[1] * self.main.card_table.size[1])

			if original_zoom != None:
				ratio = self.zoom / float(original_zoom)
				new_center = (center[0] * ratio, center[1] * ratio)
				self.set_scroll([self.total_scroll[0] + (center[0] - new_center[0]), self.total_scroll[1] + (center[1] - new_center[1])])

			self.resize_children()
			self.realign_children()
			self.flag_for_rerender()

	def mousepos_to_xcoords(self, mouse_pos):
		index = (floorint(mouse_pos[0]/self.tile_size[0]), floorint(mouse_pos[1]/self.tile_size[1]))

		center = ((index[0]+0.5)*self.tile_size[0], (index[1]+0.5)*self.tile_size[1])
		offset = ((mouse_pos[0]-center[0])/float(self.tile_size[0]),(mouse_pos[1]-center[1])/float(self.tile_size[1]))
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

	def update(self):
		if self.being_dragged or self.start_drag:
			if not self.start_drag and not self.main.mouse_button[2]:
				self.being_dragged = False
			else:
				world_pos = self.get_world_pos()
				center = (world_pos[0] + self.size[0] / 2, world_pos[1] + self.size[1] / 2)
				if not self.start_drag:
					dif = (center[0] - self.main.mouse_pos[0], center[1] - self.main.mouse_pos[1])
					self.set_scroll([self.total_scroll[0] - dif[0], self.total_scroll[1] - dif[1]])
				pygame.mouse.set_pos(center)

				self.start_drag = False
				self.being_dragged = True
			self.mouse_pos = None

	def pack(self):
		size = (self.main.card_table.size[0]*self.tile_size[0], self.main.card_table.size[1]*self.tile_size[1])
		new_scroll	=	[	min(max(self.total_scroll[0],self.tile_size[0]-size[0]),self.size[0]-self.tile_size[0]),
							min(max(self.total_scroll[1],self.tile_size[1]-size[1]),self.size[1]-self.tile_size[1])]
		if new_scroll[0] != self.total_scroll[0] or new_scroll[1] != self.total_scroll[1]:
			self.total_scroll = new_scroll
		self.realign_children()
		super(TableElement,self).pack()

	def setup_grid(self):
		#This function updates the children. Something may have been added, removed, or moved.
		#This function only takes care of the new children and the removed children.
		#This function also takes care of filling the element_table.

		new_children_list = []

		self.element_table = CardTable(self.main.card_table.size)

		removed_elements = {}

		for child in self.children:
			if type(child) == CardElement:
				removed_elements[child.card.name] = child

		#creates the new v ship cards
		for y in xrange(self.main.card_table.size[1]-1):
			for x in xrange(self.main.card_table.size[0]):
				card = self.main.card_table.v_ship_cards[y][x]
				if card != None:
					if card.name in removed_elements and removed_elements[card.name].angle == 0:
						element = removed_elements.pop(card.name)
					else:
						element = CardElement(self.main,self,None,self.card_size)
						element.set_card(card, 96)
						element.menu_info = [("Discard", self.discard_card, tuple([self.main.master_deck.cards.index(card)]))]
						element.add_handler_mousepress(self)
					self.element_table.v_ship_cards[y][x] = element
					new_children_list.append(element)

		#creates the new h ship cards
		for y in xrange(self.main.card_table.size[1]):
			for x in xrange(self.main.card_table.size[0]-1):
				card = self.main.card_table.h_ship_cards[y][x]
				if card != None:
					if card.name in removed_elements and removed_elements[card.name].angle == 90:
						element = removed_elements.pop(card.name)
					else:
						element = CardElement(self.main,self,None,[self.card_size[1],self.card_size[0]])
						element.set_card(card, 96, 90)
						element.menu_info = [("Discard", self.discard_card, tuple([self.main.master_deck.cards.index(card)]))]
						element.add_handler_mousepress(self)
					self.element_table.h_ship_cards[y][x] = element
					new_children_list.append(element)

		#creates the pony cards
		for y in xrange(self.main.card_table.size[1]):
			for x in xrange(self.main.card_table.size[0]):
				card = self.main.card_table.pony_cards[y][x]
				if card != None:
					if card.name in removed_elements:
						element = removed_elements.pop(card.name)
					else:
						element = CardElement(self.main,self,None,self.card_size)
						element.set_card(card)
						element.menu_info = [("Discard", self.discard_card, tuple([self.main.master_deck.cards.index(card)])),
											 ("Swap Card", self.swap_card, tuple([self.main.master_deck.cards.index(card)])),
											 ("Move Card", self.move_card, tuple([self.main.master_deck.cards.index(card)])),
											 ("Changeling: Imitate", self.imitate_card, tuple([self.main.master_deck.cards.index(card)])),
											 ("Ship-Effect: Make Dystopian Future Pony", self.make_dfp, tuple([self.main.master_deck.cards.index(card)])),
											 ("Ship-Effect: Make Princess", self.make_princess, tuple([self.main.master_deck.cards.index(card)])),
											 ("Ship-Effect: Swap Gender", self.swap_gender, tuple([self.main.master_deck.cards.index(card)]))]
						for t in ("Earth","Unicorn","Pegasus","Alicorn"):
							element.menu_info.append(("Ship-Effect: Change Race to "+t, self.change_race, (self.main.master_deck.cards.index(card), t.lower())))
						element.add_handler_mousepress(self)
					self.element_table.pony_cards[y][x] = element
					new_children_list.append(element)

		#we dispose of the remaining removed_elements
		keys = removed_elements.keys()
		for key in keys:
			self._remove_child(removed_elements[key])
			#del removed_elements[key]

		self.children = new_children_list

		self.realign_children()

	def resize_children(self):
		#This function is strictly for resizing existing elements.

		elements = {}
		for child in self.children:
			if type(child) == CardElement:
				elements[child.card.name] = child

		#moves the v ship cards
		for y in xrange(self.main.card_table.size[1]-1):
			for x in xrange(self.main.card_table.size[0]):
				card = self.main.card_table.v_ship_cards[y][x]
				if card != None:
					if card.name in elements:
						elements[card.name].set_size(self.card_size)

		#moves the h ship cards
		for y in xrange(self.main.card_table.size[1]):
			for x in xrange(self.main.card_table.size[0]-1):
				card = self.main.card_table.h_ship_cards[y][x]
				if card != None:
					if card.name in elements:
						elements[card.name].set_size([self.card_size[1],self.card_size[0]])

		#moves the pony cards
		for y in xrange(self.main.card_table.size[1]):
			for x in xrange(self.main.card_table.size[0]):
				card = self.main.card_table.pony_cards[y][x]
				if card != None:
					if card.name in elements:
						elements[card.name].set_size(self.card_size)

	def realign_children(self):
		#This function is strictly for moving existing elements.
		#This should only be called after resizing elements.

		elements = {}
		for child in self.children:
			if type(child) == CardElement:
				elements[child.card.name] = child

		#moves the v ship cards
		for y in xrange(self.main.card_table.size[1]-1):
			for x in xrange(self.main.card_table.size[0]):
				card = self.main.card_table.v_ship_cards[y][x]
				if card != None:
					if card.name in elements:
						elements[card.name].set_pos(self.get_graphical_pos((x,y),"v ship"))

		#moves the h ship cards
		for y in xrange(self.main.card_table.size[1]):
			for x in xrange(self.main.card_table.size[0]-1):
				card = self.main.card_table.h_ship_cards[y][x]
				if card != None:
					if card.name in elements:
						elements[card.name].set_pos(self.get_graphical_pos((x,y),"h ship"))

		#moves the pony cards
		for y in xrange(self.main.card_table.size[1]):
			for x in xrange(self.main.card_table.size[0]):
				card = self.main.card_table.pony_cards[y][x]
				if card != None:
					if card.name in elements:
						elements[card.name].set_pos(self.get_graphical_pos((x,y),"pony"))

	def rerender_foreground(self):
		if self.mouse_pos != None:
			xcoords = self.mousepos_to_xcoords(self.mouse_pos)

			#draw h ship
			info = xcoords_to_index(xcoords, "ship")
			index = info[1]
			if info[0] == "h ship":
				pos = self.get_graphical_pos(index, "h ship")
				pygame.draw.rect(self.rendered_surface, (255,0,255), (pos[0],pos[1],self.card_size[1],self.card_size[0]), 2)
			elif info[0] == "v ship":
				pos = self.get_graphical_pos(index, "v ship")
				pygame.draw.rect(self.rendered_surface, (255,0,255), (pos[0],pos[1],self.card_size[0],self.card_size[1]), 2)

			#draw pony
			info = xcoords_to_index(xcoords, "pony")
			index = info[1]
			if info[0] == "pony":
				pos = self.get_graphical_pos(index, "pony")
				pygame.draw.rect(self.rendered_surface, (127,0,255), (pos[0],pos[1],self.card_size[0],self.card_size[1]), 2)






