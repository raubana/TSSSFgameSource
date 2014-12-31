import pygame
from GUI import *

class PlayerElement(Element):
	def init(self):
		pass

	def triggerMouseHover(self, mouse_pos):
		pygame.mouse.set_cursor(*pygame.cursors.tri_left)

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