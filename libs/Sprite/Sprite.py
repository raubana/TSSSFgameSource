__author__ = 'dylan_000'

import pygame


class Sprite(object):
	def __init__(self,main,pos,size,life):
		self.main = main
		self.pos = pos
		self.size = size
		self.rendered_surface = pygame.Surface(self.size,pygame.SRCALPHA)
		self.life = life
		self.start_time = float(self.main.time)
		self.dead = False
		self.init()

	def init(self):
		pass

	def update(self):
		pass

	def move(self):
		pass

	def render(self):
		self.main.screen.blit(self.rendered_surface, self.pos)