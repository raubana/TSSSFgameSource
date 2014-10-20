import pygame
from ..GUI.GUI import *

class CardElement(Element):
	def init(self):
		self.card = None
		self.alpha = 255
		self.angle = 0

	def set_card(self, card, alpha=255, angle=0):
		self.card = card
		self.tooltip = card
		img = card.image.copy()
		if alpha < 255:
			img.fill((255,255,255,alpha),None,special_flags=BLEND_RGBA_MULT)
			self.alpha = alpha
		if angle != 0:
			img = pygame.transform.rotate(img, angle)
			self.angle = angle
		self.set_bg(ScaleImage(img, False))

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
			self.main.client.send("CLICKED_CARD:"+str(self.main.master_deck.cards.index(self.card)))
		elif button in (4,5):
			pass

	def rerender_foreground(self):
		#if self.hover:
		#	self.rendered_surface.fill((32,32,0), None, special_flags = BLEND_RGB_ADD)
		#TODO: Do a highlight to show this card is selected.
		pass
