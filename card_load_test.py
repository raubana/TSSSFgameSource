import pygame
from pygame.locals import*
pygame.init()

import math, random, time

from libs.Deck import*
from libs.locals import*

class Main(object):
    def __init__(self):
        self.screen_size = (800,600)
        self.screen = pygame.display.set_mode(self.screen_size)

        self.bg_color = (127,127,127)

        self.framerate = 1000
        self.clock = pygame.time.Clock()

        self.reset()
        self.run()

    def reset(self):
        start_time = time.time()
        self.maindeck = MasterDeck()
        self.maindeck.load_all_cards()
        end_time = time.time()

        dif = end_time - start_time
        print "Total time: "+str(dif)
        print "Number of Cards: "+str(len(self.maindeck.cards))
        print "Time per card: "+str(dif/len(self.maindeck.cards))

    def update(self):
        pass

    def move(self):
        pass

    def render(self):
        self.screen.fill(self.bg_color)

        cardsize = (CARDSIZE[0]/4,CARDSIZE[1]/4)

        x = 0
        y = 0
        for c in self.maindeck.cards:
            new_img = pygame.transform.smoothscale(c.image,cardsize)
            self.screen.blit(new_img,(x*cardsize[0],y*cardsize[1]))
            x += 1
            if (x+1)*cardsize[0] > self.screen_size[0]:
                x = 0
                y += 1

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

            self.clock.tick(self.framerate)
        pygame.quit()

main = Main()