import pygame
from ..GUI.GUI import *

class CardElement(Element):
	def set_card(self, card):
		self.card = card
		self.set_bg(ScaleImage(card.image))

	def triggerMouseHover(self, mouse_pos):
		pygame.mouse.set_cursor(*pygame.cursors.tri_left)
		#self.flag_for_rerender()

	def triggerMouseOut(self, mouse_pos):
		#self.flag_for_rerender()
		pass

	def triggerMousePressed(self, mouse_pos, button):
		if self.parent:
			corner = self.parent.get_world_pos()
		else:
			corner = (0,0)

		if button == 3:
			self.generate_context_menu((mouse_pos[0]+corner[0]+10, mouse_pos[1]+corner[1]+10))
		elif button == 1:
			pass
		elif button in (4,5):
			pass

	def rerender_foreground(self):
		#if self.hover:
		#	self.rendered_surface.fill((32,32,0), None, special_flags = BLEND_RGB_ADD)
		#TODO: Do a highlight to show this card is selected.
		pass
