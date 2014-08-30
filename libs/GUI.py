import pygame
import math


def translate_size_to_pixels(size,remaining):
	pixels = 0
	if type(size) == str:
		size = size.strip()
		if size.endswith("px"):
			pixels = int(size[-2])
		elif size.endswith("%"):
			pixels = int((float(size[:-1])*remaining)/100.0)
	elif type(size) in (float,int):
		pixels = int(size)
	else:
		raise TypeError("Not a usable type")
	return pixels


class Element(object):
	def __init__(self, main, parent, preferred_pos=None, preferred_size=None, bg_color=(255, 255, 255), always_count_hover=False):
		self.main = main
		self.element_level = parent.element_level + 1

		self.preferred_pos = preferred_pos
		self.preferred_size = preferred_size

		self.pos = None
		self.size = None
		self.padding = [0,0,0,0]

		self.rect = None

		self.rendered_surface = None

		self.bg_color = bg_color

		self.parent = parent
		if parent != self.main:
			parent._add_child(self)
		self.children = []

		self.hover = False
		self.always_count_hover = always_count_hover # This is true when it detects hovers, even when we hover over it's children.

		self.mousehover_handlers = []
		self.mousepress_handlers = []

		self.init(main)

		self.flag_for_rerender()
		self.flag_for_pack()

		self.needs_to_pack = False # This is True when this element's children need to be refitted.

	def init(self, main):
		# Here you would do any other initialization stuff you might need to do.
		#You'd want to setup this element for tick triggers in this function.
		pass

	def _add_child(self, child):
		self.children.append(child)
		self.flag_for_rerender()

	#Update For functions are called whenever this element's parent needs to update for a particular event
	def update_for_mouse_move(self, mouse_pos_local, not_hover=False):
		# We need to check if the mouse is even over our rect.
		#This returns a boolean that will be true if this element is the one that catches the event.
		#Not hover is true only if we know that there's no way this element is being hovered over.
		self_hover = False
		child_hover = False

		if not_hover:
			for c in self.children:
				c.update_for_mouse_move((mouse_pos_local[0] - self.pos[0], mouse_pos_local[1] - self.pos[1]), True)
		else:
			if self.rect.collidepoint(mouse_pos_local[0], mouse_pos_local[1]):
				#We know that at least the mouse was inside this element when it clicked.
				#The question is, did something inside of this element get hovered over?
				#In order to properly test this, we need to iterate in reverse order.
				if self.always_count_hover:
					self_hover = True
				caught = False
				i = len(self.children) - 1
				while i >= 0:
					c = self.children[i]
					caught = c.update_for_mouse_move(
						(mouse_pos_local[0] - self.pos[0], mouse_pos_local[1] - self.pos[1]), caught) or caught
					i -= 1

				if caught:
					#A child within this element caught the event.
					child_hover = True
				else:
					#Nothing else caught the event, so we catch it.
					self_hover = True
			else:
				for c in self.children:
					c.update_for_mouse_move((mouse_pos_local[0] - self.pos[0], mouse_pos_local[1] - self.pos[1]), True)
		if self.hover and not self_hover:
			self.hover = False
			self.triggerMouseOut(mouse_pos_local)
		elif not self.hover and self_hover:
			self.hover = True
			self.triggerMouseHover(mouse_pos_local)
			for handler in self.mousehover_handlers:
				handler.handle_event_mousehover(self, mouse_pos_local)
		return self_hover or child_hover

	def update_for_mouse_button_press(self, mouse_pos_local, button):
		# We need to check if the mouse is even over our rect.
		#This returns a boolean that will be true if this element is the one that catches the event.
		if self.rect.collidepoint(mouse_pos_local[0], mouse_pos_local[1]):
			#We know that at least the mouse was inside this element when it clicked.
			#The question is, did something inside of this element get clicked?
			#In order to properly test this, we need to iterate in reverse order.
			caught = False
			i = len(self.children) - 1
			while i >= 0:
				c = self.children[i]
				caught = c.update_for_mouse_button_press(
					(mouse_pos_local[0] - self.pos[0], mouse_pos_local[1] - self.pos[1]), button)
				if caught:
					break
				i -= 1
			if caught:
				#A child within this element caught the event, so we do nothing.
				pass
			else:
				#Nothing else caught the event, so we catch it.
				self.main.focus = self
				self.triggerMousePressed(mouse_pos_local, button)
				for handler in self.mousepress_handlers:
					handler.handle_event_mousepress(self, mouse_pos_local, button)
			return True

	def update_for_mouse_button_release(self, mouse_pos_local, button):
		# We need to check if the mouse is even over our rect.
		#This returns a boolean that will be true if this element is the one that catches the event.
		if self.rect.collidepoint(mouse_pos_local[0], mouse_pos_local[1]):
			#We know that at least the mouse was inside this element when it clicked.
			#The question is, did something inside of this element get clicked?
			#In order to properly test this, we need to iterate in reverse order.
			caught = False
			i = len(self.children) - 1
			while i >= 0:
				c = self.children[i]
				caught = c.update_for_mouse_button_release(
					(mouse_pos_local[0] - self.pos[0], mouse_pos_local[1] - self.pos[1]), button)
				if caught:
					break
				i -= 1
			if caught:
				#A child within this element caught the event, so we do nothing.
				pass
			else:
				#Nothing else caught the event, so we catch it.
				self.triggerMouseRelease(mouse_pos_local, button)
			return True

	def update_for_keydown(self, key):
		pass

	def update_for_keyup(self, key):
		pass

	#Handle functions are called when something handles another element's caught events.
	def handle_event_mousehover(self, widget, mouse_pos_local):
		pass

	def handle_event_mousepress(self, widget, mouse_pos_local, button):
		pass

	#Add Handler functions allow other elements to catch events that this element catches
	def add_handler_mousehover(self, handler):
		self.mousehover_handlers.append(handler)

	def add_handler_mousepress(self, handler):
		self.mousepress_handlers.append(handler)

	#Triggers are called when an event is caught by this element
	def triggerMouseHover(self, mouse_pos):
		pass

	def triggerMouseOut(self, mouse_pos):
		pass

	def triggerMousePressed(self, mouse_pos, button):
		pass

	def triggerMouseRelease(self, mouse_pos, button):
		pass

	def update(self):
		pass

	def set_size(self, new_size):
		if new_size != self.preferred_size:
			self.preferred_size = new_size
			self.flag_for_pack()

	def set_pos(self, new_pos):
		if new_pos != self.preferred_pos:
			self.preferred_pos = new_pos
			self.flag_for_pack()

	def get_local_pos(self):
		return (float(self.pos[0]), float(self.pos[1]))

	def get_world_pos(self):
		# this is recursive
		if self.parent == self.main:
			offset = (0, 0)
		else:
			offset = self.parent.get_world_pos()
		return (self.pos[0] + offset[0], self.pos[1] + offset[1])

	def set_bg_color(self, new_bg_color):
		if new_bg_color != self.bg_color:
			self.bg_color = new_bg_color
			self.flag_for_rerender()

	def update_rect(self):
		self.rect = pygame.Rect([self.pos[0], self.pos[1], self.size[0], self.size[1]])

	def flag_for_rerender(self):
		if self.parent != self.main:
			self.parent.flag_for_rerender()
		self.needs_to_rerender = True

	def flag_for_pack(self):
		self.parent._setup_for_pack()

	def _setup_for_pack(self):
		#THIS SHOULD NOT BE CALLED UNLESS YOU KNOW WHAT YOU'RE DOING!!
		if not self.needs_to_pack:
			self.needs_to_pack = True
			level_name = str(self.element_level)
			if level_name not in self.main.elements_to_pack:
				level = []
				self.main.elements_to_pack[level_name] = level
			else:
				level = self.main.elements_to_pack[level_name]
			level.append(self)

	def pack(self):
		#This is the function called to resize and reorganize an element's children.
		#You should override this function if this element doesn't organize it's elements in this way.
		if self.needs_to_pack: # NECESSARY
			self.needs_to_pack = False # NECESSARY
			#In this case, our pack function will order our elements using a flow layout
			x_pos = 0
			y_pos = 0
			x_remaining = int(self.size[0])
			y_remaining = int(self.size[1])
			y_needed = 0
			#The flow layout tries to fill a single row until no more children can be added because the element isn't
			# wide enough, at which point a new row is used below it.
			for child in self.children:
				#We need to determine this child's new size
				size = (max(translate_size_to_pixels(child.preferred_size[0],x_remaining),0),
						max(translate_size_to_pixels(child.preferred_size[1],y_remaining),0))
				new_pos = (int(x_pos+child.padding[0]),int(y_pos+child.padding[1]))
				new_size = 	(int(size[0]), int(size[1]))

				if new_pos[0] + new_size[0] + child.padding[0] + child.padding[2] > self.size[0]:
					x_pos = 0

					x_remaining = int(self.size[0])
					y_remaining -= y_needed
					y_pos += y_needed
					y_needed = 0

					size = (max(translate_size_to_pixels(child.preferred_size[0],x_remaining),0),
						max(translate_size_to_pixels(child.preferred_size[1],y_remaining),0))
					new_pos = (int(x_pos+child.padding[0]),int(y_pos+child.padding[1]))
					new_size = (int(size[0]), int(size[1]))

				x_pos += new_size[0] + child.padding[0] + child.padding[2]
				x_remaining -= new_size[0] + child.padding[0] + child.padding[2]
				y_needed = max(size[1] + child.padding[1] + child.padding[3], y_needed)

				redo= False
				if new_pos != child.pos:
					redo = True
					child.pos = new_pos
				if new_size != child.size:
					redo = True
					child.size = new_size
					child._setup_for_pack()
				if redo:
					child.update_rect()
					child.flag_for_rerender()

	def rerender(self):
		# this is redrawing it's elements to the rendered surface
		if self.needs_to_rerender:
			self.needs_to_rerender = False
			if self.parent == self.main:
				self.rendered_surface = self.main.screen
			else:
				if self.rendered_surface == None or self.size != self.rendered_surface.get_size():
					self.rendered_surface = pygame.Surface(self.size,pygame.SRCALPHA)
			if self.bg_color != None:
				self.rendered_surface.fill(self.bg_color)
			for child in self.children:
				child.render()

	def render(self):
		self.rerender()
		if self.parent != self.main:
			self.parent.rendered_surface.blit(self.rendered_surface, self.pos)