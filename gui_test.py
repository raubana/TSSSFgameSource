import pygame
from pygame.locals import*
pygame.init()

import math, random, time

from libs.GUI import*

class TestElement(Element):
    def triggerMouseHover(self,mouse_pos):
        self.set_bg_color((255,255,0))

    def triggerMouseOut(self,mouse_pos):
        self.set_bg_color((127,127,0))

    def triggerMousePressed(self,mouse_pos,button):
        self.set_bg_color((0,255,0))

    def triggerMouseRelease(self,mouse_pos,button):
        self.set_bg_color((255,0,0))


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
        self.updated_elements = []

        e1 = TestElement(self,(0,0),(self.screen_size[0],200),None)
        e2 = TestElement(self,(100,25),(100,100),e1)
        e3 = TestElement(self,(25,25),(25,25),e2)

        e4 = TestElement(self,(75,75),(50,50),e1)

        self.elements = [e1]

    def update(self):
        for e in self.events:
            if e.type == MOUSEMOTION:
                for element in self.elements:
                    element.update_for_mouse_move(self.mouse_pos)
            elif e.type == MOUSEBUTTONDOWN:
                    for element in self.elements:
                        element.update_for_mouse_button_press(self.mouse_pos,e.button)
            elif e.type == MOUSEBUTTONUP:
                    for element in self.elements:
                        element.update_for_mouse_button_release(self.mouse_pos,e.button)

        for element in self.updated_elements:
            element.update()

    def move(self):
        pass

    def render(self):
        self.screen.fill(self.bg_color)
        for element in self.elements:
            element.render()
            self.screen.blit(element.rendered_surface,element.pos)
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