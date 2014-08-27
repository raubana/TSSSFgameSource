import pygame
from pygame.locals import*
pygame.init()

import libs.netcom as netcom

##########

server = netcom.Server(netcom.gethostname(), 27015)

screen = pygame.display.set_mode((800,600))
clock = pygame.time.Clock()

running = True
while running:
	events = pygame.event.get()

	for client in server.clients.keys():
		if len(server.received_messages[client]) > 0:
			message = server.received_messages[client].pop(0)
			print "CLIENT '"+client+"' SAYS: '"+message+"'"

	for e in events:
		if e.type == QUIT or e.type == KEYDOWN and e.key == K_ESCAPE:
			running = False

	pygame.display.flip()
	clock.tick(12)

pygame.quit()
server.close()