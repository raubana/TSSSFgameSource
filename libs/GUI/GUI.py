import pygame
from pygame.locals import*

from ..locals import *
from ..common import lerp, invlerp

def translate_size_to_pixels(size,remaining):
	pixels = 0
	if type(size) == str:
		size = size.replace(" ","")
		if "-" in size:
			parts = size.split("-")
			p1 = translate_size_to_pixels(parts[0],remaining)
			p2 = translate_size_to_pixels(parts[1],remaining)
			pixels = p1 - p2
		else:
			if size.endswith("px"):
				pixels = int(size[:-2])
			elif size.endswith("%"):
				pixels = int((float(size[:-1])*remaining)/100.0)
	elif type(size) in (float,int):
		pixels = int(size)
	else:
		raise TypeError("Not a usable type")
	return pixels


class Element(object):
	def __init__(self, main, parent, preferred_pos=None, preferred_size=None, bg_color=(255, 255, 255), text_color=(0,0,0), always_count_hover=False):
		self.main = main
		self.element_level = parent.element_level + 1

		self.preferred_pos = preferred_pos
		self.preferred_size = preferred_size

		self.pos = None
		self.size = None
		self.padding = [0,0,0,0]
		self.margin = [0,0,0,0]
		self.layout = LAYOUT_FLOW

		self.rect = None

		self.rendered_surface = None

		self.bg_color = bg_color
		self.text_color = text_color

		self.text = ""
		self.text_align = ALIGN_TOPLEFT
		self.font = self.main.font

		self.v_scrollable = False
		self.h_scrollable = False

		self.v_scrollbar = None
		self.h_scrollbar = None

		self.always_show_v_scroll = False
		self.always_show_h_scroll = False

		self.parent = parent
		if parent != self.main:
			parent._add_child(self)
		self.children = []

		self.hover = False
		self.always_count_hover = always_count_hover # This is true when it detects hovers, even when we hover over it's children.

		self.mousehover_handlers = []
		self.mousepress_handlers = []
		self.getfocus_handlers = []
		self.losefocus_handlers = []
		self.keydown_handlers = []

		self.init()

		self.flag_for_rerender()
		self.flag_for_pack()

		self.needs_to_pack = False # This is True when this element's children need to be refitted.

	def __del__(self):
		if self.main.focus == self:
			self.unfocus()

	def init(self):
		# Here you would do any other initialization stuff you might need to do.
		#You'd want to setup this element for tick triggers in this function.
		pass

	def _add_child(self, child):
		self.children.append(child)
		child.flag_for_pack()
		self.flag_for_rerender()

	def _remove_child(self, child):
		self.children.remove(child)
		self._setup_for_pack()
		self.flag_for_rerender()

	def clear(self):
		#This removes every child from this element.
		while len(self.children) > 0:
			if self.main.focus == self.children[0]:
				self.children[0].unfocus()
			del self.children[0]
		self.layout = LAYOUT_FLOW

	def give_focus(self):
		if self.main.focus != None:
			self.main.focus.unfocus()
		self.main.focus = self
		self.triggerGetFocus()
		for handler in self.losefocus_handlers:
			handler.handle_event_getfocus(self)

	def unfocus(self):
		if self.main.focus == self:
			self.main.focus = None
			self.triggerLoseFocus()
			for handler in self.losefocus_handlers:
				handler.handle_event_losefocus(self)

	#Update For functions are called whenever this element's parent needs to update for a particular event
	def update_for_mouse_move(self, mouse_pos_local, not_hover=False):
		# We need to check if the mouse is even over our rect.
		#This returns a boolean that will be true if this element is the one that catches the event.
		#Not hover is true only if we know that there's no way this element is being hovered over.
		self_hover = False
		child_hover = False
		self.triggerMouseMove(mouse_pos_local)
		if not_hover:
			for c in self.children:
				if c is not None:
					c.update_for_mouse_move((mouse_pos_local[0] - self.pos[0], mouse_pos_local[1] - self.pos[1]), True)
		else:
			if self.rect != None and self.rect.collidepoint(mouse_pos_local[0], mouse_pos_local[1]):
				#We know that at least the mouse was inside this element when it clicked.
				#The question is, did something inside of this element get hovered over?
				#In order to properly test this, we need to iterate in reverse order.
				if self.always_count_hover:
					self_hover = True
				caught = False
				i = len(self.children) - 1
				while i >= 0:
					c = self.children[i]
					if c is not None:
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
					if c is not None:
						c.update_for_mouse_move((mouse_pos_local[0] - self.pos[0], mouse_pos_local[1] - self.pos[1]), True)
		if self.hover and not self_hover:
			self.hover = False
			self.triggerMouseOut(mouse_pos_local)
		elif not self.hover and self_hover:
			self.hover = True
			pygame.mouse.set_cursor(*pygame.cursors.arrow)
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
				if c is not None:
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
				if button in (1,2,3):
					self.give_focus()
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
				if c is not None:
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

	def update_for_keydown(self, unicode, key):
		self.triggerKeyDown(unicode, key)
		for handler in self.keydown_handlers:
			handler.handle_event_keydown(self, unicode, key)

	def update_for_keyup(self, key):
		pass

	#Handle functions are called when something handles another element's caught events.
	def handle_event_mousehover(self, widget, mouse_pos_local):
		pass

	def handle_event_mousepress(self, widget, mouse_pos_local, button):
		pass

	def handle_event_getfocus(self, widget):
		pass

	def handle_event_losefocus(self, widget):
		pass

	def handle_event_scroll(self, widget, amount):
		if widget in (self.h_scrollbar, self.v_scrollbar):
			self._setup_for_pack()

	#Add Handler functions allow other elements to catch events that this element catches
	def add_handler_keydown(self, handler):
		self.keydown_handlers.append(handler)

	def add_handler_mousehover(self, handler):
		self.mousehover_handlers.append(handler)

	def add_handler_mousepress(self, handler):
		self.mousepress_handlers.append(handler)

	def add_handler_getfocus(self, handler):
		self.getfocus_handlers.append(handler)

	def add_handler_losefocus(self, handler):
		self.losefocus_handlers.append(handler)

	#Triggers are called when an event is caught by this element
	def triggerKeyDown(self, unicode, key):
		pass

	def triggerMouseMove(self, mouse_pos):
		pass

	def triggerMouseHover(self, mouse_pos):
		pass

	def triggerMouseOut(self, mouse_pos):
		pass

	def triggerMousePressed(self, mouse_pos, button):
		pass

	def triggerMouseRelease(self, mouse_pos, button):
		pass

	def triggerGetFocus(self):
		pass

	def triggerLoseFocus(self):
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

	def set_text(self, new_text):
		if new_text != self.text:
			self.text = new_text
			self.flag_for_rerender()

	def set_text_align(self, new_align):
		if new_align != self.text_align:
			self.text_align = new_align
			self.flag_for_rerender()

	def set_text_color(self, new_color):
		if new_color != self.text_color:
			self.text_color = new_color
			self.flag_for_rerender()

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
		if self.layout == LAYOUT_SPLIT:
			if self.needs_to_pack: # NECESSARY
				self.needs_to_pack = False # NECESSARY
				# This is a unique layout where the first 4 children fill the outside (left,top,right,bottom)
				# and the 5th fills the center. Any other child after that is treated as a absolute element.

				min_x = 0
				min_y = 0
				max_x = self.size[0]
				max_y = self.size[1]

				#First, we must check that all children exist:
				if len(self.children) < 5:
					raise LookupError("There must be no less than 5 children for a split layout to function")

				#First, we take care of our left child, which fills the entire left side of the element
				child = self.children[0]
				if child != None:
					size = (max(translate_size_to_pixels(child.preferred_size[0],max_x-min_x),0),
											max(translate_size_to_pixels("100%",max_y-min_y),0))
					new_pos = (int(0+child.margin[0]+child.padding[0]),int(0+child.margin[1]+child.padding[1]))
					new_size = 	(max(int(size[0]-child.padding[0]-child.padding[2]),1), max(int(size[1]-child.padding[1]-child.padding[3]),1))
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
					min_x = child.pos[0]+new_size[0]+child.padding[2]+child.margin[2]
				#next, we take care of our right child, which fills the entire right side of the element
				child = self.children[2]
				if child != None:
					size = (max(translate_size_to_pixels(child.preferred_size[0],max_x-min_x),0),
											max(translate_size_to_pixels("100%",max_y-min_y),0))
					new_size = 	(max(int(size[0]-child.padding[0]-child.padding[2]),1), max(int(size[1]-child.padding[1]-child.padding[3]),1))
					new_pos = (int(max_x - new_size[0] - child.margin[2]), int(0+child.margin[1]+child.padding[1]))
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
					max_x = child.pos[0]-child.padding[0]-child.margin[0]
				#next we take care of our top child, which fills the top area between the left and right children
				child = self.children[1]
				if child != None:
					size = (max(translate_size_to_pixels("100%",max_x-min_x),0),
											max(translate_size_to_pixels(child.preferred_size[1],max_y-min_y),0))
					new_size = 	(max(int(size[0]-child.padding[0]-child.padding[2]),1), max(int(size[1]-child.padding[1]-child.padding[3]),1))
					new_pos = (int(min_x + child.padding[0] + child.margin[0]), int(min_y + child.padding[0] + child.margin[0]))
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
					min_y = child.pos[1]+child.size[1]+child.padding[3]+child.margin[3]
				#next we take care of our bottom child, which fills the bottom area between the left and right children
				child = self.children[3]
				if child != None:
					size = (max(translate_size_to_pixels("100%",max_x-min_x),0),
											max(translate_size_to_pixels(child.preferred_size[1],max_y-min_y),0))
					new_size = 	(max(int(size[0]-child.padding[0]-child.padding[2]),1), max(int(size[1]-child.padding[1]-child.padding[3]),1))
					new_pos = (int(min_x + child.padding[0] + child.margin[0]), int(max_y - new_size[1] - child.margin[3]))
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
					max_y = child.pos[1]-child.padding[1]-child.margin[1]
				#finally, we add in our last element which fills the gap between the first 4 children
				child = self.children[4]
				if child != None:
					size = (max(translate_size_to_pixels(child.preferred_size[0],max_x-min_x),0),
											max(translate_size_to_pixels(child.preferred_size[1],max_y-min_y),0))
					new_pos = (int(min_x + child.padding[0] + child.margin[0]), int(min_y + child.padding[1] + child.margin[1]))
					new_size = 	(max(int(size[0]-child.padding[0]-child.padding[2]),1), max(int(size[1]-child.padding[1]-child.padding[3]),1))
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
				#lastly, we do absolute positioning for the remaining children
				for child in self.children[5:]:
					size = (max(translate_size_to_pixels(child.preferred_size[0],self.size[0]),0),
											max(translate_size_to_pixels(child.preferred_size[1],self.size[0]),0))
					if child.preferred_pos == None:
						pos = (0,0)
					else:
						pos = child.preferred_pos
					new_pos = (int(pos[0] + child.padding[0] + child.margin[0]), int(pos[1] + child.padding[1] + child.margin[1]))
					new_size = 	(max(int(size[0]-child.padding[0]-child.padding[2]),1), max(int(size[1]-child.padding[1]-child.padding[3]),1))
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

		else:
			offset = [0,0]
			if self.h_scrollbar != None:
				offset[0] = -self.h_scrollbar.scrolled_amount
			if self.v_scrollbar != None:
				offset[1] = -self.v_scrollbar.scrolled_amount

			if self.needs_to_pack: # NECESSARY
				self.needs_to_pack = False # NECESSARY
				#In this case, our pack function will order our elements using a flow layout
				x_pos = 0
				y_pos = 0
				x_remaining = int(self.size[0])
				y_remaining = int(self.size[1])
				y_needed = 0
				x_max = 0
				y_max = 0
				#The flow layout tries to fill a single row until no more children can be added because the element isn't
				# wide enough, at which point a new row is used below it.
				for child in self.children:
					if child is not None and child not in (self.v_scrollbar, self.h_scrollbar):
						if self.layout == LAYOUT_FLOW:
							#We need to determine this child's new size
							size = (max(translate_size_to_pixels(child.preferred_size[0],x_remaining),0),
									max(translate_size_to_pixels(child.preferred_size[1],y_remaining),0))
							new_pos = (int(x_pos+child.margin[0]+child.padding[0]),int(y_pos+child.margin[1]+child.padding[1]))
							new_size = 	(max(int(size[0]-child.padding[0]-child.padding[2]),1), max(int(size[1]-child.padding[1]-child.padding[3]),1))

							if new_pos[0] + new_size[0] + child.margin[0] + child.margin[2] + child.padding[2] > self.size[0]:
								x_pos = 0

								x_remaining = int(self.size[0])
								y_remaining -= y_needed
								y_pos += y_needed
								y_needed = 0

								size = (max(translate_size_to_pixels(child.preferred_size[0],x_remaining),0),
									max(translate_size_to_pixels(child.preferred_size[1],y_remaining),0))
								new_pos = (int(x_pos+child.margin[0]+child.padding[0]),int(y_pos+child.margin[1]+child.padding[1]))
								new_size = 	(max(int(size[0]-child.padding[0]-child.padding[2]),1), max(int(size[1]-child.padding[1]-child.padding[3]),1))

							x_pos += new_size[0] + child.margin[0] + child.margin[2] + child.padding[0] + child.padding[2]
							x_remaining -= new_size[0] + child.margin[0] + child.margin[2] + child.padding[0] + child.padding[2]
							y_needed = max(new_size[1] + child.margin[1] + child.margin[3] + child.padding[1] + child.padding[3], y_needed)

							x_max = max(x_max,x_pos)
							y_max = max(y_max,y_pos+y_needed)
						elif self.layout == LAYOUT_VERTICAL:
							#We need to determine this child's new size
							size = (max(translate_size_to_pixels(child.preferred_size[0],x_remaining),0),
									max(translate_size_to_pixels(child.preferred_size[1],y_remaining),0))
							new_pos = (int(x_pos+child.margin[0]+child.padding[0]),int(y_pos+child.margin[1]+child.padding[1]))
							new_size = 	(max(int(size[0]-child.padding[0]-child.padding[2]),1), max(int(size[1]-child.padding[1]-child.padding[3]),1))
							y_pos += new_size[1] + child.margin[1] + child.margin[3] + child.padding[1] + child.padding[3]

							x_max = max(x_max,new_size[0] + child.margin[0] + child.margin[2] + child.padding[0] + child.padding[2])
							y_max = max(y_max,y_pos)
						elif self.layout == LAYOUT_HORIZONTAL:
							#We need to determine this child's new size
							size = (max(translate_size_to_pixels(child.preferred_size[0],x_remaining),0),
									max(translate_size_to_pixels(child.preferred_size[1],y_remaining),0))
							new_pos = (int(x_pos+child.margin[0]+child.padding[0]),int(y_pos+child.margin[1]+child.padding[1]))
							new_size = 	(max(int(size[0]-child.padding[0]-child.padding[2]),1), max(int(size[1]-child.padding[1]-child.padding[3]),1))
							x_pos += new_size[0] + child.margin[0] + child.margin[2] + child.padding[0] + child.padding[2]

							x_max = max(x_max,x_pos)
							y_max = max(y_max,new_size[0] + child.margin[0] + child.margin[2] + child.padding[0] + child.padding[2])

						new_pos = (new_pos[0]+offset[0], new_pos[1]+offset[1])

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

				#We setup our scroll bars now
				if self.v_scrollable:
					#We check if we've exceeded our vertical limit
					v_dif = (self.size[1]-SCROLLBAR_WIDTH) - y_max
					if v_dif < 0 or self.always_show_v_scroll:
						#we will need the vertical scrollbar, so we check if one already exists, otherwise we create one
						if self.v_scrollbar == None:
							self.v_scrollbar = ScrollBar(self.main, self, None, None)
							self.v_scrollbar.add_handler_scroll(self)
						#we setup the scrollbar to scroll the proper amounts
						self.v_scrollbar.set_scroll_range(0,max(-v_dif,0))
						#we also set the scrollbar to be in the proper location
						self.v_scrollbar.pos = (self.size[0]-SCROLLBAR_WIDTH,0)
						new_size = (SCROLLBAR_WIDTH,self.size[1])
						if new_size != self.v_scrollbar.size:
							self.v_scrollbar.size = new_size
							self.v_scrollbar.flag_for_rerender()
						self.v_scrollbar.update_rect()
						#we need to make sure that our scrollbar is at the top of the children list
						self.children.remove(self.v_scrollbar)
						self.children.append(self.v_scrollbar)
					else:
						#We no longer need the vertical scrollbar, so we remove it.
						if self.v_scrollbar != None:
							self.children.remove(self.v_scrollbar)
							self.v_scrollbar = None
							self._setup_for_pack()

				if self.h_scrollable:
					#We check if we've exceeded our horizontal limit
					h_dif = (self.size[0]-SCROLLBAR_WIDTH) - x_max
					if h_dif < 0 or self.always_show_h_scroll:
						#we will need the horizontal scrollbar, so we check if one already exists, otherwise we create one
						if self.h_scrollbar == None:
							self.h_scrollbar = ScrollBar(self.main, self, None, None)
							self.h_scrollbar.scroll_direction = SCROLLBAR_HORIZONTAL
							self.h_scrollbar.add_handler_scroll(self)
						#we setup the scrollbar to scroll the proper amounts
						self.h_scrollbar.set_scroll_range(0,max(-h_dif,0))
						#we also set the scrollbar to be in the proper location
						self.h_scrollbar.pos = (0,self.size[1]-SCROLLBAR_WIDTH)
						if self.v_scrollable:
							new_size = (max(self.size[0]-SCROLLBAR_WIDTH,1),SCROLLBAR_WIDTH)
						else:
							new_size = (self.size[0],SCROLLBAR_WIDTH)
						if new_size != self.h_scrollbar.size:
							self.h_scrollbar.size = new_size
							self.h_scrollbar.flag_for_rerender()
						self.h_scrollbar.update_rect()
						#we need to make sure that our scrollbar is at the top of the children list
						self.children.remove(self.h_scrollbar)
						self.children.append(self.h_scrollbar)
					else:
						#We no longer need the horizontal scrollbar, so we remove it.
						if self.h_scrollbar != None:
							self.children.remove(self.h_scrollbar)
							self.h_scrollbar = None
							self._setup_for_pack()


	def rerender_background(self):
		if self.bg_color != None:
			self.rendered_surface.fill(self.bg_color)
		else:
			self.rendered_surface.fill((0,0,0,0))

	def rerender_text(self):
		if self.text != "":
			img = self.font.render(self.text,True,self.text_color)
			if self.text_align == ALIGN_TOPLEFT:
				rect = img.get_rect(topleft = (0,0))
			elif self.text_align == ALIGN_MIDDLE:
				rect = img.get_rect(center = (self.size[0]/2,self.size[1]/2))
			self.rendered_surface.blit(img, rect)

	def rerender_foreground(self):
		pass

	def rerender_children(self):
		for child in self.children:
			if child is not None:
				child.render()

	def rerender(self):
		# this is redrawing it's elements to the rendered surface
		if self.needs_to_rerender:
			self.needs_to_rerender = False
			if self.parent == self.main:
				self.rendered_surface = self.main.screen
			else:
				if self.rendered_surface == None or self.size != self.rendered_surface.get_size():
					try:
						self.rendered_surface = pygame.Surface(self.size,pygame.SRCALPHA)
					except Exception, e:
						print self.size
						raise e
			self.rerender_background()
			self.rerender_foreground()
			self.rerender_text()
			self.rerender_children()

	def render(self):
		self.rerender()
		if self.parent != self.main:
			self.parent.rendered_surface.blit(self.rendered_surface, self.pos)


class InputBox(Element):
	def init(self):
		self.index = 0
		self.offset = 0
		self.cursor_pos = 0

		self.max_characters = None
		self.legal_characters = PRINTABLE_CHARS

		self.valuechange_handlers = []
		self.submit_handlers = []

	def add_handler_valuechange(self, handler):
		self.valuechange_handlers.append(handler)

	def add_handler_submit(self, handler):
		self.submit_handlers.append(handler)

	def update_for_keydown(self, unicode, key):
		prev_value = str(self.text)
		#first we check if it's a printable character
		if key == K_DELETE or key == K_BACKSPACE:
			#We remove a character to the left of this index.
			if self.index > 0:
				self.text = self.text[:max(self.index-1,0)] + self.text[self.index:]
				self.index -= 1
				self.flag_for_rerender()
		elif key in (K_LEFT, K_RIGHT):
			if key == K_LEFT: self.index -= 1
			else: self.index += 1
			self.index = min(max(self.index,0),len(self.text))
			self.flag_for_rerender()
		elif key == K_RETURN:
			self.update_for_submit()
		elif (unicode in (u"",u" ") and key == K_SPACE) or (unicode not in (u"",u" ") and unicode in self.legal_characters and unicode in PRINTABLE_CHARS):
			#We know this is printable, so we add this character to the string.
			if self.max_characters == None or len(self.text) < self.max_characters:
				self.text = self.text[:self.index] + unicode + self.text[self.index:]
				self.index += 1
				self.flag_for_rerender()

		#we check if our cursor is still visible
		while True:
			self.cursor_pos = self.main.font.size(self.text[:self.index])[0] - self.main.font.size(self.text[:self.offset])[0]
			if self.cursor_pos < 0:
				self.offset -= 1
			elif self.cursor_pos > self.size[0]-4:
				self.offset += 1
			else:
				break

		if prev_value != self.text:
			self.update_for_valuechange()

	def triggerMouseHover(self, mouse_pos):
		pygame.mouse.set_cursor(*pygame.cursors.tri_left)

	def triggerGetFocus(self):
		self.flag_for_rerender()

	def triggerLoseFocus(self):
		self.flag_for_rerender()

	def triggerValueChange(self):
		pass

	def triggerSubmit(self):
		pass

	def update_for_valuechange(self):
		self.triggerValueChange()
		for handler in self.valuechange_handlers:
			handler.handle_event_valuechange(self)

	def update_for_submit(self):
		self.triggerSubmit()
		for handler in self.submit_handlers:
			handler.handle_event_submit(self)

	def rerender_foreground(self):
		pygame.draw.lines(self.rendered_surface, (self.bg_color[0]/4,self.bg_color[1]/4,self.bg_color[2]/4), False, [(0,self.size[1]),(0,0),(self.size[0],0)])
		pygame.draw.lines(self.rendered_surface, (self.bg_color[0]/2,self.bg_color[1]/2,self.bg_color[2]/2), False, [(0,self.size[1]-1),(self.size[0]-1,self.size[1]-1),(self.size[0]-1,0)])

	def rerender_text(self):
		img = self.main.font.render(self.text[max(self.offset,0):],True,self.text_color)
		self.rendered_surface.blit(img,(2,2))

		if self.main.focus == self:
			pos = self.cursor_pos
			pygame.draw.line(self.rendered_surface, (127,0,0), (pos+2,2), (pos+2,self.size[1]-4))


class Button(Element):
	def init(self):
		self.submit_handlers = []
		self.text_align = ALIGN_MIDDLE

	def add_handler_submit(self, handler):
		self.submit_handlers.append(handler)

	def update_for_submit(self):
		self.triggerSubmit()
		for handler in self.submit_handlers:
			handler.handle_event_submit(self)

	def triggerSubmit(self):
		pass

	def triggerMousePressed(self, mouse_pos, button):
		self.update_for_submit()

	def triggerMouseHover(self, mouse_pos):
		pygame.mouse.set_cursor(*pygame.cursors.tri_left)

	def rerender_text(self):
		img = self.main.font.render(self.text, True, self.text_color)
		rect = img.get_rect(center = (self.size[0]/2,self.size[1]/2))
		self.rendered_surface.blit(img, rect)

	def rerender_background(self):
		if self.bg_color != None:
			self.rendered_surface.fill((self.bg_color[0]/2,self.bg_color[1]/2,self.bg_color[2]/2))

	def rerender_foreground(self):
		pygame.draw.lines(self.rendered_surface, (self.bg_color[0],self.bg_color[1],self.bg_color[2]), False, [(0,self.size[1]),(0,0),(self.size[0],0)], 1)
		pygame.draw.lines(self.rendered_surface, (self.bg_color[0]/4,self.bg_color[1]/4,self.bg_color[2]/4), False, [(0,self.size[1]-1),(self.size[0]-1,self.size[1]-1),(self.size[0]-1,0)], 1)


class ScrollBar(Element):
	def init(self):
		self.grabbed = False
		self.scroll_direction = SCROLLBAR_VERTICAL
		self.scrolled_amount = 0
		self.min_scroll = 0
		self.max_scroll = 10

		self.scroll_handlers = []

	def add_handler_scroll(self, handler):
		self.scroll_handlers.append(handler)

	def update_for_scroll(self, amount):
		self.triggerScroll(amount)
		for handler in self.scroll_handlers:
			handler.handle_event_scroll(self, amount)

	def triggerMousePressed(self, mouse_pos, button):
		if button == 1:
			self.grabbed = True

	def triggerMouseMove(self, mouse_pos):
		if self.grabbed:
			if self.min_scroll < self.max_scroll:
				if self.scroll_direction == SCROLLBAR_HORIZONTAL:
					size = self.size[0]
					pos = mouse_pos[0]
				else:
					size = self.size[1]
					pos = mouse_pos[1]
				pos = min(max(pos,0),size)
				size = float(size)
				self.set_scrolled_amount(int(lerp(self.min_scroll,self.max_scroll,invlerp(0,size,pos))))
			if not self.main.mouse_button[0]:
				self.grabbed = False

	def triggerMouseHover(self, mouse_pos):
		pygame.mouse.set_cursor(*pygame.cursors.tri_left)

	def triggerScroll(self, amount):
		pass

	def set_scroll_range(self, mins, maxs):
		if mins != self.min_scroll or maxs != self.max_scroll:
			self.min_scroll = mins
			self.max_scroll = maxs
			if self.scrolled_amount < self.min_scroll or self.scrolled_amount > self.max_scroll:
				self.set_scrolled_amount(min(max(self.scrolled_amount,self.min_scroll),self.max_scroll))
			self.flag_for_rerender()

	def set_scrolled_amount(self, amount):
		if amount != self.scrolled_amount:
			self.update_for_scroll(amount)
			self.scrolled_amount = amount
			self.flag_for_rerender()

	def flag_for_pack(self):
		pass

	def _setup_for_pack(self):
		pass

	def rerender_background(self):
		if self.bg_color != None:
			self.rendered_surface.fill((self.bg_color[0]/2,self.bg_color[1]/2,self.bg_color[2]/2,127))

	def rerender_foreground(self):
		pygame.draw.rect(self.rendered_surface,(self.bg_color[0]/2,self.bg_color[1]/2,self.bg_color[2]/2),(0,0,self.size[0],self.size[1]),1)
		#pygame.draw.lines(self.rendered_surface, (self.bg_color[0]/4,self.bg_color[1]/4,self.bg_color[2]/4), False, [(0,self.size[1]),(0,0),(self.size[0],0)])
		#pygame.draw.lines(self.rendered_surface, (self.bg_color[0]/2,self.bg_color[1]/2,self.bg_color[2]/2), False, [(0,self.size[1]-1),(self.size[0]-1,self.size[1]-1),(self.size[0]-1,0)])
		if self.min_scroll < self.max_scroll:
			bar_size = SCROLLBAR_BAR_MINSIZE
			if self.scroll_direction == SCROLLBAR_HORIZONTAL:
				size = (bar_size,SCROLLBAR_WIDTH-2)
				pos = (int(lerp(1,self.size[0]-bar_size-1,invlerp(self.min_scroll,self.max_scroll,float(self.scrolled_amount)))), 1)
			else:
				size = (SCROLLBAR_WIDTH-2,bar_size)
				pos = (1,int(lerp(1,self.size[1]-bar_size-1,invlerp(self.min_scroll,self.max_scroll,float(self.scrolled_amount)))))
			pygame.draw.rect(self.rendered_surface,self.bg_color,(pos[0],pos[1],size[0],size[1]))

