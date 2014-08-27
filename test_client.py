import pygame
from pygame.locals import*
pygame.init()

import libs.netcom as netcom

from libs.Deck import*
from libs.locals import*
from libs.PickledCard import*

import io

##########

screen = pygame.display.set_mode((800,600))
clock = pygame.time.Clock()

client = netcom.Client("71.10.148.168", 27015)

running = True
while running:
	events = pygame.event.get()

	img = None

	if len(client.received_messages) > 0:
		message = client.received_messages.pop(0)
		if message.beginswith("CARD:"):
			print "RECEIVED CARD FROM THE SERVER!"
			message = message[len("CARD:"):]
			f = open_pickledcard(io.BytesIO(message))
			card = Card()
			card.parsePickledCard(f)
			img = card.image
		else:
			print "SERVER SAYS: '"+message+"'"

	for e in events:
		if e.type == QUIT or e.type == KEYDOWN and e.key == K_ESCAPE:
			running = False
		else:
			if e.type == KEYDOWN:
				if e.key == K_SPACE:
					client.send("THIS IS A MESSAGE FROM THE CLIENT!!")
				elif e.key == K_p:
					print("Sending request for random card...")
					client.send("Gimme a random card.")

	screen.fill((0,0,0))

	if img != None:
		screen.blit(img,(0,0))

	pygame.display.flip()
	clock.tick(12)

pygame.quit()
client.close()
