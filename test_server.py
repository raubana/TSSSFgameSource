import pygame
from pygame.locals import*
pygame.init()

import libs.netcom as netcom

##########

print "THIS SERVER'S EXTERNAL IP IS: "
print netcom.get_this_computers_external_address()
print

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
		else:
			if e.type == KEYDOWN:
				if e.key == K_SPACE:
					server.sendall("THIS IS A MESSAGE FROM THE SERVER!!")

	pygame.display.flip()
	clock.tick(12)

pygame.quit()
server.close()