import pygame
import pygame.freetype
from pygame.locals import*
pygame.init()


screen_size = (800,600)
screen = pygame.display.set_mode(screen_size)

font = pygame.font.Font("data/fonts/Ubahn_newpony.ttf",40)
ft_font = pygame.freetype.Font("data/fonts/Ubahn_newpony.ttf",40)

running = True
while running:
	events = pygame.event.get()

	screen.fill((0,0,0))

	text = "This is a string."

	srf1 = font.render(text,True,(255,0,0))
	rect1 = srf1.get_rect(topleft = (0,0))
	screen.blit(srf1,rect1)

	data2 = ft_font.render(text,(0,255,0))
	srf2 = data2[0]
	rect2 = data2[1]
	rect3 = srf2.get_rect()
	screen.blit(srf2,(rect2.left,ft_font.get_sized_height()-ft_font.get_sized_ascender()))
	print ft_font.get_sized_height(), ft_font.get_sized_ascender(), ft_font.get_sized_descender()
	print rect2, rect3

	pygame.display.flip()

	for event in events:
		if event.type == QUIT or event.type == KEYDOWN and event.key == K_ESCAPE:
			running = False

pygame.quit()