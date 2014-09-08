__author__ = 'dylan_000'

from Sprite import*

class ChatSprite(Sprite):
	def set_text(self, message, color=(0,0,0,255), bg_color=(255,255,255,127)):
		self.rendered_surface = pygame.Surface(self.main.font.size(message),pygame.SRCALPHA)
		self.rendered_surface.fill(bg_color)
		self.rendered_surface.blit(self.main.font.render(message, True, color),(0,0))
		self.size = self.rendered_surface.get_size()

	def update(self):
		if self.main.time >= self.life + self.start_time:
			self.dead = True