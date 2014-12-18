import pygame
from GUI import *
from ..GUI.CardElement import *
from ..common import *
from ..CardTable import xcoords_to_index


class TableElement(Element):
	def init(self):
		self.main.updated_elements.append(self)

		self.mouse_pos = None
		self.total_offset = [0,0]
		self.total_scroll = [0,0]
		self.total_size = [0,0]

		self.zoom = None
		self.set_zoom(0.15)

		self.being_dragged = False
		self.start_drag = False

	def set_scroll(self, new_scroll):
		new_scroll = (int(new_scroll[0]),int(new_scroll[1]))
		if new_scroll != self.total_scroll:
			self.total_scroll = new_scroll
			self.flag_for_rerender()

	def triggerMousePressed(self, mouse_pos, button):
		if button == 1:
			pass
		elif button == 3:
			self.start_drag = True
		elif button in (4, 5):
			world_pos = self.get_world_pos()
			pos = (mouse_pos[0] - world_pos[0] - self.total_scroll[0], mouse_pos[1] - world_pos[1] - self.total_scroll[1])
			if button == 4:
				self.zoom_in(pos)
			else:
				self.zoom_out(pos)

	def zoom_in(self, center=None):
		new_zoom = self.zoom + 0.15
		self.set_zoom(new_zoom, center)

	def zoom_out(self, center=None):
		new_zoom = self.zoom - 0.15
		self.set_zoom(new_zoom, center)

	def set_zoom(self, new_zoom, center=None, force=False):
		if center == None:
			center = (0, 0)

		new_zoom = min(max(new_zoom, 0.15), 0.6)

		if new_zoom != self.zoom or force:
			if self.zoom != None:
				original_zoom = float(self.zoom)
			else:
				original_zoom = None

			self.zoom = new_zoom
			self.card_size = (int(CARD_SIZE[0] * self.zoom), int(CARD_SIZE[1] * self.zoom))
			self.tile_size = (int(CARD_SIZE[0] * self.zoom * 1.25), int(CARD_SIZE[1] * self.zoom * 1.25))

			self.total_size = (self.tile_size[0] * self.main.card_table.size[0], self.tile_size[1] * self.main.card_table.size[1])

			if original_zoom != None:
				ratio = self.zoom / float(original_zoom)
				new_center = (center[0] * ratio, center[1] * ratio)
				self.set_scroll([self.total_scroll[0] + (center[0] - new_center[0]), self.total_scroll[1] + (center[1] - new_center[1])])

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

	def rerender_foreground(self):
		grid_size = (self.size[0] / self.tile_size[0] + 2, self.size[1] / self.tile_size[1] + 2)
		offset = (self.total_scroll[0]%self.tile_size[0], self.total_scroll[1]%self.tile_size[1])
		grid_start = ( 	-(self.total_scroll[0]/self.tile_size[0]) - 1 ,
						-(self.total_scroll[1]/self.tile_size[1]) - 1 )

		#first we draw the grid
		for y in xrange(grid_size[1]):
			for x in xrange(grid_size[0]):
				index = (x+grid_start[0],y+grid_start[1])
				if index[0] >= 0 and index[0] <= self.main.card_table.size[0] - 1 and index[1] >= 0 and index[1] <= self.main.card_table.size[1] - 1:
					if (x + self.total_offset[0] + grid_start[0]) % 2 == (y + self.total_offset[1] + grid_start[1]) % 2:
						color = (198, 185, 224, 255)
					else:
						color = (179, 173, 227, 255)
					pygame.draw.rect(self.rendered_surface,
									 color,
									 ((x-1)*self.tile_size[0]+offset[0],
									  (y-1)*self.tile_size[1]+offset[1],
									  self.tile_size[0],
									  self.tile_size[1]))

		#next we draw the pony cards
		for y in xrange(grid_size[1]):
			for x in xrange(grid_size[0]):
				index = (x+grid_start[0],y+grid_start[1])
				if index[0] >= 0 and index[0] <= self.main.card_table.size[0] - 1 and index[1] >= 0 and index[1] <= self.main.card_table.size[1] - 1:
					card = self.main.card_table.pony_cards[index[0]][index[1]]
					if card != None:
						img = pygame.transform.smoothscale(card.get_image(), self.card_size)
						rect = img.get_rect(center = ((x-1+0.5)*self.tile_size[0]+offset[0],
													  (y-1+0.5)*self.tile_size[1]+offset[1]))
						self.rendered_surface.blit(img,rect)

		pygame.draw.circle(self.rendered_surface, (255,0,0), (int(self.total_scroll[0]),int(self.total_scroll[1])), 3)

	def setup_grid(self):
		print "SETUP GRID WAS CALLED!"
		self.flag_for_rerender()
