import pygame
from pygame.locals import*
pygame.init()

import libs.netcom as netcom

##########

client = netcom.Client("71.10.148.168", 27015)

screen = pygame.display.set_mode((800,600))
clock = pygame.time.Clock()

running = True
while running:
	events = pygame.event.get()

	if len(client.received_messages[client]) > 0:
		message = client.received_messages[client].pop(0)
		print "SERVER '"+client+"' SAYS: '"+message+"'"

	for e in events:
		if e.type == QUIT or e.type == KEYDOWN and e.key == K_ESCAPE:
			running = False
		else:
			if e.type == KEYDOWN:
				if e.key == K_SPACE:
					client.send("THIS IS A MESSAGE FROM THE CLIENT!!")

	pygame.display.flip()
	clock.tick(12)

pygame.quit()
client.close()
