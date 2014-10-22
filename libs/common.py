import pygame
from pygame.locals import *

pygame.init()

import math

IMG_SHADOW_CORNER = pygame.image.load("imgs/misc/shadow/corner.png")
IMG_SHADOW_SIDE = pygame.image.load("imgs/misc/shadow/side.png")


def floorint(x):
	return int(math.floor(x))


def lerp(a, b, p):
	return a + (b - a) * p


def lerp_colors(a, b, p):
	return (int(lerp(a[0], b[0], p)), int(lerp(a[1], b[1], p)), int(lerp(a[2], b[2], p)))


def invlerp(a, b, x):
	return (x - a) / (b - a)


def apply_shadow(srf, size, alpha=127):
	img = pygame.Surface((srf.get_width() + size * 2, srf.get_height() + size * 2), SRCALPHA)
	img.fill((255, 255, 255, 0))
	img.blit(srf, (size, size))

	corner = pygame.transform.smoothscale(IMG_SHADOW_CORNER, (size, size))
	corner.fill((255, 255, 255, alpha), None, special_flags = BLEND_RGBA_MULT )
	img.blit(corner, (0,0))
	corner = pygame.transform.flip(corner, True, False)
	img.blit(corner, (srf.get_width() + size, 0))
	corner = pygame.transform.flip(corner, False, True)
	img.blit(corner, (srf.get_width() + size, srf.get_height() + size))
	corner = pygame.transform.flip(corner, True, False)
	img.blit(corner, (0, srf.get_height() + size))

	v_side = pygame.transform.smoothscale(IMG_SHADOW_SIDE, (size, srf.get_height()))
	v_side.fill((255, 255, 255, alpha), None, special_flags = BLEND_RGBA_MULT )
	img.blit(v_side, (0, size))
	v_side = pygame.transform.flip(v_side, True, False)
	img.blit(v_side, (size+srf.get_width(), size))

	h_side = pygame.transform.smoothscale(IMG_SHADOW_SIDE, (size, srf.get_width()))
	h_side.fill((255, 255, 255, alpha), None, special_flags = BLEND_RGBA_MULT )
	h_side = pygame.transform.rotate(h_side, -90)
	img.blit(h_side, (size, 0))
	h_side = pygame.transform.flip(h_side, False, True)
	img.blit(h_side, (size, size + srf.get_height()))

	return img