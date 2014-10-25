import pygame
from pygame.locals import *

pygame.init()

from libs.PickledCard import *
import libs.Deck
from libs.locals import *


class Main(object):
	def __init__(self):
		self.screen_size = (800, 600)
		self.screen = pygame.display.set_mode(self.screen_size)

		self.bg_color = (127, 127, 127)

		self.framerate = 60
		self.clock = pygame.time.Clock()

		print "A"
		self.card = libs.Deck.Card()
		self.card.parsePickledCard(open_pickledcard("data/default_cards/PonyChangelingEarth.tsssf"))

		print "B"
		self.imit_card = libs.Deck.Card()
		#self.imit_card.parsePickledCard(open_pickledcard("data/default_cards/PonyApplejackTheCutestSmartestAllaroundbestBackgroundPony.tsssf"))
		self.imit_card.parsePickledCard(open_pickledcard("data/default_cards/PonyBraeburn.tsssf"))

		print "C"

		self.index = 0

		self.reset()
		self.run()

	def reset(self):
		self.card.imitate_card(self.imit_card)

		self.card.set_temp_name("Braeburn", "Totally Braeburn")

		self.card.rerender()
		#pygame.image.save(self.card.image, "stills/"+str(self.index)+".png")
		#self.index += 1

	def update(self):
		pass

	def move(self):
		pass

	def render(self):
		self.screen.fill(self.bg_color)

		cardsize = (CARD_SIZE[0], CARD_SIZE[1])

		new_img = pygame.transform.smoothscale(self.card.get_image(), cardsize)
		self.screen.blit(new_img, (0,0))

		pygame.display.flip()

	def run(self):
		self.running = True
		while self.running:
			self.mouse_pos = pygame.mouse.get_pos()
			self.mouse_button = pygame.mouse.get_pressed()
			self.events = pygame.event.get()

			self.update()
			self.move()
			self.render()

			for e in self.events:
				if e.type == QUIT or e.type == KEYDOWN and e.key == K_ESCAPE:
					self.running = False
				elif e.type == KEYDOWN and e.key == K_r:
					self.reset()

			self.clock.tick(self.framerate)
		pygame.quit()


main = Main()