import pygame
import math

class Element(object):
    def __init__(self,main,pos,size,parent,bg_color=(255,255,255),always_count_hover=False):
        self.pos = pos
        self.size = size
        self.update_rect()

        self.bg_color = bg_color

        self.parent = parent
        if parent != None:
            parent.add_child(self)
        self.children = []

        self.hover = False
        self.always_count_hover = always_count_hover#This is true when it detects hovers, even when we hover over it's children.

        self.needs_to_rerender = True #redundent, but it's here.
        self.rendered_surface = pygame.Surface(size,pygame.SRCALPHA)

        self.mousehover_handlers = []
        self.mousepress_handlers = []

        self.init(main)
        self.rerender()

    def init(self,main):
        #Here you would do any other initialization stuff you might need to do.
        #You'd want to setup this element for tick triggers in this function.
        pass

    def add_child(self,child):
        self.children.append(child)
        self.flag_for_rerender()

    def update_for_mouse_move(self,mouse_pos_local,not_hover=False):
        #We need to check if the mouse is even over our rect.
        #This returns a boolean that will be true if this element is the one that catches the event.
        #Not hover is true only if we know that there's no way this element is being hovered over.
        self_hover = False
        child_hover = False

        if not_hover:
            for c in self.children:
                c.update_for_mouse_move((mouse_pos_local[0]-self.pos[0],mouse_pos_local[1]-self.pos[1]),True)
        else:
            if self.rect.collidepoint(mouse_pos_local[0],mouse_pos_local[1]):
                #We know that at least the mouse was inside this element when it clicked.
                #The question is, did something inside of this element get hovered over?
                #In order to properly test this, we need to iterate in reverse order.
                if self.always_count_hover:
                    self_hover = True
                caught = False
                i = len(self.children)-1
                while i >= 0:
                    c = self.children[i]
                    caught = c.update_for_mouse_move((mouse_pos_local[0]-self.pos[0],mouse_pos_local[1]-self.pos[1]), caught) or caught
                    i -= 1

                if caught:
                    #A child within this element caught the event.
                    child_hover = True
                else:
                    #Nothing else caught the event, so we catch it.
                    self_hover = True
            else:
                for c in self.children:
                    c.update_for_mouse_move((mouse_pos_local[0]-self.pos[0],mouse_pos_local[1]-self.pos[1]),True)
        if self.hover and not self_hover:
            self.hover = False
            self.triggerMouseOut(mouse_pos_local)
        elif not self.hover and self_hover:
            self.hover = True
            self.triggerMouseHover(mouse_pos_local)
            for handler in self.mousehover_handlers:
                handler.handle_event_mousehover(self,mouse_pos_local)
        return self_hover or child_hover

    def handle_event_mousehover(self,widget,mouse_pos_local):
        pass

    def update_for_mouse_button_press(self,mouse_pos_local,button):
        #We need to check if the mouse is even over our rect.
        #This returns a boolean that will be true if this element is the one that catches the event.
        if self.rect.collidepoint(mouse_pos_local[0],mouse_pos_local[1]):
            #We know that at least the mouse was inside this element when it clicked.
            #The question is, did something inside of this element get clicked?
            #In order to properly test this, we need to iterate in reverse order.
            caught = False
            i = len(self.children)-1
            while i >= 0:
                c = self.children[i]
                caught = c.update_for_mouse_button_press((mouse_pos_local[0]-self.pos[0],mouse_pos_local[1]-self.pos[1]),button)
                if caught:
                    break
                i -= 1
            if caught:
                #A child within this element caught the event, so we do nothing.
                pass
            else:
                #Nothing else caught the event, so we catch it.
                self.triggerMousePressed(mouse_pos_local, button)
                for handler in self.mousepress_handlers:
                    handler.handle_event_mousepress(self,mouse_pos_local,button)
            return True

    def handle_event_mousepress(self,widget,mouse_pos_local,button):
        pass

    def update_for_mouse_button_release(self,mouse_pos_local,button):
        #We need to check if the mouse is even over our rect.
        #This returns a boolean that will be true if this element is the one that catches the event.
        if self.rect.collidepoint(mouse_pos_local[0],mouse_pos_local[1]):
            #We know that at least the mouse was inside this element when it clicked.
            #The question is, did something inside of this element get clicked?
            #In order to properly test this, we need to iterate in reverse order.
            caught = False
            i = len(self.children)-1
            while i >= 0:
                c = self.children[i]
                caught = c.update_for_mouse_button_release((mouse_pos_local[0]-self.pos[0],mouse_pos_local[1]-self.pos[1]),button)
                if caught:
                    break
                i -= 1
            if caught:
                #A child within this element caught the event, so we do nothing.
                pass
            else:
                #Nothing else caught the event, so we catch it.
                self.triggerMouseRelease(mouse_pos_local, button)
            return True

    def add_handler_mousehover(self,handler):
        self.mousehover_handlers.append(handler)

    def add_handler_mousepress(self,handler):
        self.mousepress_handlers.append(handler)

    def triggerMouseHover(self,mouse_pos):
        pass

    def triggerMouseOut(self,mouse_pos):
        pass

    def triggerMousePressed(self,mouse_pos,button):
        pass

    def triggerMouseRelease(self,mouse_pos,button):
        pass

    def update(self):
        pass

    def set_size(self,new_size):
        if new_size != self.size:
            self.size = new_size
            self.rendered_surface = pygame.Surface(new_size,pygame.SRCALPHA)
            self.update_rect()
            self.flag_for_rerender()

    def set_pos(self, new_pos):
        if new_pos != self.pos:
            self.pos = new_pos
            self.update_rect()
            if self.parent != None:
                self.parent.flag_for_rerender()

    def get_local_pos(self):
        return (float(self.pos[0]),float(self.pos[1]))

    def get_world_pos(self):
        #this is recursive
        if self.parent == None:
            offset = (0,0)
        else:
            offset = self.parent.get_world_pos()
        return (self.pos[0]+offset[0],self.pos[1]+offset[1])

    def set_bg_color(self,new_bg_color):
        if new_bg_color != self.bg_color:
            self.bg_color = new_bg_color
            self.flag_for_rerender()

    def update_rect(self):
        self.rect = pygame.Rect([self.pos[0],self.pos[1],self.size[0],self.size[1]])

    def flag_for_rerender(self):
        if self.parent != None:
            self.parent.flag_for_rerender()
        self.needs_to_rerender = True

    def rerender(self):
        #this is redrawing it's elements to the rendered surface
        self.needs_to_rerender = False
        if self.bg_color != None:
            self.rendered_surface.fill(self.bg_color)
        #pygame.draw.rect(self.rendered_surface,(self.bg_color[0]/2,self.bg_color[1]/2,self.bg_color[2]),[0,0,self.size[0],self.size[1]],1)
        for child in self.children:
            child.render()

    def render(self):
        if self.needs_to_rerender:
            self.rerender()
        if self.parent != None:
            self.parent.rendered_surface.blit(self.rendered_surface,self.pos)


class ImageElement(Element):
    def __init__(self,main,pos,size,parent,surface,always_count_hover=False):
        self.pos = pos
        self.size = size
        self.update_rect()

        self.surface = surface

        self.parent = parent
        if parent != None:
            parent.add_child(self)
        self.children = []

        self.hover = False
        self.always_count_hover = always_count_hover#This is true when it detects hovers, even when we hover over it's children.

        self.needs_to_rerender = True #redundent, but it's here.
        self.rendered_surface = pygame.Surface(size,pygame.SRCALPHA)

        self.init(main)
        self.rerender()

    def rerender(self):
        #this is redrawing it's elements to the rendered surface
        self.needs_to_rerender = False
        self.rendered_surface = pygame.transform.smoothscale(self.surface, self.size)
        for child in self.children:
            child.render()