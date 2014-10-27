import pygame
from pygame.locals import*
pygame.init()

from libs.locals import *

surfaces = []

try:
	while True:
		surfaces.append(pygame.Surface(CARD_SIZE, SRCALPHA))
except:
	pass

print "HIT MAX."
print "COUNT: "+str(len(surfaces))