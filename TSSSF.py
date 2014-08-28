import pygame
from pygame.locals import *
pygame.init()

import numpy

import math, random, time

from libs.GUI import *


class Main(object):
	def __init__(self):
		self.screen_size = (854,480)
		self.screen = pygame.display.set_mode(self.screen_size,RESIZABLE)

		self.framerate = 60
		self.clock = pygame.time.Clock()

		self.stills = []
		self.still_freq = 1 / 10.0
		self.last_still = time.time() - self.still_freq

		self.reset()
		self.run()

	def reset(self):
		self.controller = None  # Controllers are used to control the application while something is being taken care of.

		# SETS UP THE GUI
		self.updated_elements = []
		self.main_element = Element(self, (0, 0), self.screen_size, None, always_count_hover=True)
		self.focus = None

	def update(self):
		for e in self.events:
			if e.type == MOUSEMOTION:
				self.main_element.update_for_mouse_move(e.pos)
			elif e.type == MOUSEBUTTONDOWN:
				self.main_element.update_for_mouse_button_press(e.pos, e.button)
			elif e.type == MOUSEBUTTONUP:
				self.main_element.update_for_mouse_button_release(e.pos, e.button)

			elif e.type == KEYDOWN:
				if self.focus != None:
					self.focus.update_for_keydown(e.key)
			elif e.type == KEYUP:
				if self.focus != None:
					self.focus.update_for_keyup(e.key)

			elif e.type == VIDEORESIZE:
				self.screen_size = self.screen.get_size()
				self.main_element.set_size(self.screen_size)

		for element in self.updated_elements:
			element.update()

		if self.controller != None:
			self.controller.update()

	def move(self):
		if self.controller != None:
			self.controller.move()

	def render(self):
		self.main_element.rendered_surface = self.screen
		self.main_element.render()

		if self.controller != None:
			self.controller.render()

		pygame.display.flip()

		"""
		if self.time > self.last_still+self.still_freq:
			self.last_still = float(self.time)
			copy = self.screen.copy()
			temp = pygame.Surface((10,10))
			temp.fill((255,255,255))
			temp.blit(copy,(5-self.mouse_pos[0],5-self.mouse_pos[1]),special_flags = BLEND_RGB_SUB)
			copy.blit(temp,(self.mouse_pos[0]-5,self.mouse_pos[1]-5))
			self.stills.append(copy)
		"""

	def run(self):
		self.running = True
		while self.running:
			self.time = time.time()
			self.keys = list(pygame.key.get_pressed())
			self.mouse_pos = pygame.mouse.get_pos()
			self.mouse_button = pygame.mouse.get_pressed()
			self.events = pygame.event.get()

			self.update()
			self.move()
			self.render()

			for e in self.events:
				if e.type == QUIT or e.type == KEYDOWN and e.key == K_ESCAPE:
					self.running = False

			self.clock.tick(self.framerate)

		for i in xrange(len(self.stills)):
			pygame.image.save(self.stills[i], "stills/" + str(len(self.stills) - i) + ".bmp")

		pygame.quit()


main = Main()