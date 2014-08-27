import pygame
from pygame.locals import*
pygame.init()

import libs.netcom as netcom

from libs.Deck import*
from libs.locals import*
from libs.PickledCard import*

import io
import random

##########

print "THIS SERVER'S EXTERNAL IP IS: "
print netcom.get_this_computers_external_address()
print

screen = pygame.display.set_mode((800,600))
clock = pygame.time.Clock()

print "LOADING THE DECK..."
deck = MasterDeck()
deck.load_all_cards()

server = netcom.Server(netcom.gethostname(), 27015)

running = True
while running:
	events = pygame.event.get()

	for client in server.clients.keys():
		if len(server.received_messages[client]) > 0:
			message = server.received_messages[client].pop(0)
			print "CLIENT '"+client+"' SAYS: '"+message+"'"

			if message == "Gimme a random card.":
				print "I guess I gotta snag some card to send..."
				card = random.choice(deck.pc_cards)
				server.sendto(client,"CARD:"+card)

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