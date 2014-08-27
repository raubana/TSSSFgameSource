import pygame
from pygame.locals import*
pygame.init()
import numpy

import math, random, time

from libs.GUI import*
from libs.common import*
from libs.locals import*

import libs.Deck as deck

class PlayerHandElement(Element):
    def init(self,main):
        self.main = main
        main.updated_elements.append(self)
        self.always_count_hover = True

        self.start_time = 0
        self.start_height = 0
        self.target_height = int(self.start_height)

        self.duration = 0.1

        self.children_order = []

        self.selected_index = -1

        self.overlap_percent = 0.1
        self.card_width = (self.size[0]-(10*2)-(10*(7-1)))/float(7)
        self.card_width = lerp(self.card_width, self.size[0]-(10*2), self.overlap_percent)
        self.card_height = CARDSIZE[1]*(self.card_width/CARDSIZE[0])
        self.card_size = (int(self.card_width),int(self.card_height))

        self.set_size((self.size[0], self.card_height + 30))
        self.set_pos((0,self.main.screen_size[1]))

    def set_target_height(self,target_height):
        if self.target_height != target_height:
            self.start_time = float(self.main.time)
            self.start_height = self.main.screen_size[1]-self.pos[1]
            self.target_height = target_height

    def add_card(self,card):
        child = CardElement(self.main,(0,0),CARDSIZE,self,card)
        child.add_handler_mousehover(self)
        child.add_handler_mousepress(self)

    def update_hand(self):
        self.children = []
        self.children_order = []
        for c in self.main.player_hand.cards:
            self.add_card(c)
        self.flag_for_rerender()

    def add_child(self,child):
        self.selected_index = -1
        self.children_order.append(child)
        self.resort_children()
        self.flag_for_rerender()

    def triggerMouseHover(self,mouse_pos):
        self.start_time = time.time()
        self.start_height = self.size[1]
        self.flag_for_rerender()

    def triggerMouseOut(self,mouse_pos):
        if self.selected_index != -1:
            self.resort_children(self.selected_index)
        self.flag_for_rerender()

    def triggerMousePressed(self,mouse_pos,button):
        if self.selected_index != -1:
            self.selected_index = -1
            self.realign_children()

    def resort_children(self,index = None):
        self.children = []

        if index == None:
            index = len(self.children_order) - 1

        for i in xrange(len(self.children_order)):
            i1 = i - (len(self.children_order)-index)
            i2 = index + len(self.children_order) - 1 - i

            if i1 >= 0 and i1 < len(self.children_order):
                self.children.append(self.children_order[i1])
                p = i1/float(max(len(self.children_order),7)-1)
                self.children_order[i1].set_pos((int(lerp(self.last_card_pos+10,10,p)),20-10*(i1 == self.selected_index)))
                self.children_order[i1].set_size(self.card_size)

            if i2 >= 0 and i2 < len(self.children_order) and i1 != i2:
                self.children.append(self.children_order[i2])
                p = i2/float(max(len(self.children_order),7)-1)
                self.children_order[i2].set_pos((int(lerp(self.last_card_pos+10,10,p)),20-10*(i2 == self.selected_index)))
                self.children_order[i2].set_size(self.card_size)
        self.flag_for_rerender()

    def realign_children(self):
        for child in self.children:
            child.set_pos((child.pos[0],20-10*(self.selected_index != -1 and child == self.children_order[self.selected_index])))
        self.flag_for_rerender()

    def handle_event_mousehover(self,widget,mouse_pos_local):
        index = self.children_order.index(widget)
        self.resort_children(index)

    def handle_event_mousepress(self,widget,mouse_pos_local,button):
        new_index = self.selected_index
        if button == 1:
            new_index = self.children_order.index(widget)
            if new_index == self.selected_index:
                new_index = -1
        elif button == 3:
            new_index = -1

        if new_index != self.selected_index:
            self.selected_index = new_index
            if self.selected_index != -1:
                self.resort_children(self.selected_index)
                #self.main.selected_card = self.children_order[self.selected_index].card
            else:
                self.realign_children()
                #self.main.selected_card = None
            self.flag_for_rerender()

    def update(self):
        if self.hover:
            target_height = self.card_height + 30
        elif self.main.cardtable_element.being_dragged:
            target_height = 0
        else:
            target_height = max(self.card_height*0.2+20,25)

        self.set_target_height(target_height)

        dif = float(self.main.time) - self.start_time
        if dif > self.duration:
            p = 1.0
        else:
            p = dif/self.duration

        width = self.main.screen_size[0]-self.main.right_gui.size[0]
        height = int(lerp(self.start_height,self.target_height,p))

        self.set_pos((0,self.main.screen_size[1]-height))

        self.last_card_pos = self.size[0]-(2*10)-self.card_size[0]

    def rerender(self):
        #this is redrawing it's elements to the rendered surface
        self.needs_to_rerender = False
        if self.bg_color != None:
            self.rendered_surface.fill(self.bg_color)
        #pygame.draw.rect(self.rendered_surface,(self.bg_color[0]/2,self.bg_color[1]/2,self.bg_color[2]),[0,0,self.size[0],self.size[1]],1)
        if len(self.children) > 0:
            if self.hover or self.selected_index != -1:
                for child in self.children[:-1]:
                    child.render()
                self.rendered_surface.fill((127,127,127),None,special_flags = BLEND_RGB_MULT)
                self.children[-1].render()
            else:
                for child in self.children:
                    child.render()


class EndTurnButton(Element):
    def init(self,main):
        self.main = main
        self.enabled = True
        self.normal_bg_color = (255,127,127)
        self.disable()

    def enable(self):
        if not self.enabled:
            self.enabled = True
            self.set_bg_color((self.normal_bg_color[0]/2,self.normal_bg_color[1]/2,self.normal_bg_color[2]/2))

    def disable(self):
        if self.enabled:
            self.enabled = False
            self.set_bg_color((self.normal_bg_color[0]/3+64,self.normal_bg_color[1]/3+64,self.normal_bg_color[2]/3+64))

    def triggerMouseHover(self,mouse_pos):
        if self.enabled:
            self.set_bg_color(self.normal_bg_color)

    def triggerMouseOut(self,mouse_pos):
        if self.enabled:
            self.set_bg_color((self.normal_bg_color[0]/2,self.normal_bg_color[1]/2,self.normal_bg_color[2]/2))

    def triggerMousePressed(self,mouse_pos,button):
        pass


class RightGuiElement(Element):
    #This element is designed to automaticly reorder elements verticaly, plus resize their widths to 100%
    def init(self,main):
        main.updated_elements.append(self)

    def update(self):
        y_pos = 0
        for child in self.children:
            child.set_pos((0,y_pos))
            child.set_size((self.size[0],child.size[1]))
            y_pos += child.size[1]


class ScrollableGoalsGuiElement(Element):
    #This element is designed to automaticly resize
    def init(self,main):
        main.updated_elements.append(self)

    def update(self):
        y_pos = 0
        for child in self.children:
            child.set_pos((0,y_pos))
            y_pos += child.size[1]


class CardElement(ImageElement):
    def __init__(self,main,pos,size,parent,card,image=None,always_count_hover=False):
        self.pos = pos
        self.size = size
        self.update_rect()

        self.card = card
        if image == None:
            self.surface = card.image.copy()
        else:
            self.surface = image

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

        self.main = main

        self.init(main)
        self.rerender()

    def triggerMousePressed(self,mouse_pos,button):
        if button == 1:
            self.set_as_selected_card()

    def set_as_selected_card(self):
        if self.main.selected_card_element != None:
            self.main.selected_card_element.flag_for_rerender()
        self.main.selected_card_element = self
        self.flag_for_rerender()

    def triggerMouseHover(self,mouse_pos):
        self.main.set_hover_card(self.card)

    def triggerMouseOut(self,mouse_pos):
        self.main.unset_hover_card(self.card)

    def rerender(self):
        #this is redrawing it's elements to the rendered surface
        self.needs_to_rerender = False
        self.rendered_surface = pygame.transform.smoothscale(self.surface,self.size)
        if self.main.selected_card_element != None and self.main.selected_card_element.card == self.card:
            pygame.draw.rect(self.rendered_surface,(255,255,0),(0,0,self.size[0]-1,self.size[1]-1),2)
        for child in self.children:
            child.render()


class CardTableElement(Element):
    def init(self,main):
        self.main = main
        self.main.updated_elements.append(self)
        self.zoom = None
        self.set_zoom(0.15)

        self.total_offset = [0,0]

        self.being_dragged = False
        self.start_drag = False

        self.parent.add_handler_mousepress(self)

        self.corner_grad = pygame.image.load("imgs/gradients/grad_corner.png")
        self.side_grad = pygame.image.load("imgs/gradients/grad_side.png")

    def handle_event_mousepress(self,widget,mouse_pos_local,button):
        self.triggerMousePressed((mouse_pos_local[0]+self.pos[0],mouse_pos_local[1]+self.pos[1]),button)

    def triggerMousePressed(self,mouse_pos,button):
        if button == 1:
            pass
        elif button == 3:
            self.start_drag = True
        elif button in (4,5):
            if button == 4:
                self.zoom_in((mouse_pos[0]-self.pos[0],mouse_pos[1]-self.pos[1]))
            else:
                self.zoom_out((mouse_pos[0]-self.pos[0],mouse_pos[1]-self.pos[1]))

    def zoom_in(self,center = None):
        new_zoom = self.zoom + 0.15
        self.set_zoom(new_zoom,center)

    def zoom_out(self,center = None):
        new_zoom = self.zoom - 0.15
        self.set_zoom(new_zoom,center)

    def update(self):
        if self.being_dragged or self.start_drag:
            if not self.start_drag and not self.main.mouse_button[2]:
                self.being_dragged = False
            else:
                world_pos = self.parent.get_world_pos()
                center = (world_pos[0]+self.parent.size[0]/2, world_pos[1]+self.parent.size[1]/2)
                if not self.start_drag:
                    dif = (center[0]-self.main.mouse_pos[0],center[1]-self.main.mouse_pos[1])
                    self.set_pos((self.pos[0]+dif[0],self.pos[1]+dif[1]))
                pygame.mouse.set_pos(center)

                self.start_drag = False
                self.being_dragged = True

    def set_pos(self, new_pos):
        #we have to clamp this so this element doesn't go off screen
        new_pos = (min(max(new_pos[0],self.tile_size[0]-self.size[0]),self.parent.size[0]-self.tile_size[0]),
                    min(max(new_pos[1],self.tile_size[1]-self.size[1]),self.parent.size[1]-self.tile_size[1]))
        if new_pos != self.pos:
            self.pos = new_pos
            self.update_rect()
            if self.parent != None:
                self.parent.flag_for_rerender()

    def update_table(self):
        if self.main.selected_card_element != None and self.main.selected_card_element in self.children:
            selected_card = self.main.selected_card_element.card
        else:
            selected_card = None

        self.children = []
        #we need to change our size

        #first we do the ship cards
        #lets to the horizontal ships first
        for y in xrange(self.main.cardtable.size[1]):
            for x in xrange(self.main.cardtable.size[0]-1):
                card = self.main.cardtable.h_ship_cards[y][x]
                if card != None:
                    scale = round(self.zoom*100)
                    key = card.name + ", " + str(scale)+"%"
                    if key in self.main.cards_scaled_images:
                        img = self.main.cards_scaled_images[key]
                    else:
                        img = pygame.transform.smoothscale(card.image,self.card_size)
                        self.main.cards_scaled_images[key] = img.copy()
                    img = pygame.transform.rotate(img,90)
                    rect = img.get_rect( center = (self.tile_size[0]*(x+1.0),self.tile_size[1]*(y+1.5)) )
                    child = CardElement(self.main,rect.topleft,rect.size,self,card,image = img)
                    child.flag_for_rerender()
                    child.add_handler_mousepress(self)
                    if card == selected_card:
                        child.set_as_selected_card()

        #then the vertical ships
        for y in xrange(self.main.cardtable.size[1]-1):
            for x in xrange(self.main.cardtable.size[0]):
                card = self.main.cardtable.v_ship_cards[y][x]
                if card != None:
                    scale = round(self.zoom*100)
                    key = card.name + ", " + str(scale)+"%"
                    if key in self.main.cards_scaled_images:
                        img = self.main.cards_scaled_images[key].copy()
                    else:
                        img = pygame.transform.smoothscale(card.image,self.card_size)
                        self.main.cards_scaled_images[key] = img.copy()
                    rect = img.get_rect( center = (self.tile_size[0]*(x+1.5),self.tile_size[1]*(y+1.0)) )
                    child = CardElement(self.main,rect.topleft,rect.size,self,card,image=img)
                    child.flag_for_rerender()
                    child.add_handler_mousepress(self)
                    if card == selected_card:
                        child.set_as_selected_card()

        #lastly the pony cards
        for y in xrange(self.main.cardtable.size[1]):
            for x in xrange(self.main.cardtable.size[0]):
                card = self.main.cardtable.pony_cards[y][x]
                if card != None:
                    scale = round(self.zoom*100)
                    key = card.name + ", " + str(scale)+"%"
                    if key in self.main.cards_scaled_images:
                        img = self.main.cards_scaled_images[key].copy()
                    else:
                        img = pygame.transform.smoothscale(card.image,self.card_size)
                        self.main.cards_scaled_images[key] = img.copy()
                    rect = img.get_rect( center = (self.tile_size[0]*(x+0.5),self.tile_size[1]*(y+0.5)) )
                    child = CardElement(self.main,rect.topleft,rect.size,self,card,image=img)
                    child.flag_for_rerender()
                    child.add_handler_mousepress(self)
                    if card == selected_card:
                        child.set_as_selected_card()

    def set_zoom(self, new_zoom, center = None, force=False):
        if center == None:
            center = (0,0)

        new_zoom = min(max(new_zoom,0.15),0.45)

        if new_zoom != self.zoom or force:
            if self.zoom != None:
                original_zoom = float(self.zoom)
            else:
                original_zoom = None

            self.zoom = new_zoom
            self.card_size = (int(CARDSIZE[0]*self.zoom), int(CARDSIZE[1]*self.zoom))
            self.tile_size = (int(CARDSIZE[0]*self.zoom*1.25), int(CARDSIZE[1]*self.zoom*1.25))

            self.set_size((self.tile_size[0]*self.main.cardtable.size[0],self.tile_size[1]*self.main.cardtable.size[1]))

            if original_zoom != None:
                ratio = self.zoom/float(original_zoom)
                new_center = (center[0]*ratio,center[1]*ratio)
                self.set_pos((self.pos[0]+(center[0]-new_center[0]),self.pos[1]+(center[1]-new_center[1])))

            self.update_table()

    def rerender(self):
        #this is redrawing it's elements to the rendered surface
        self.needs_to_rerender = False
        #self.rendered_surface.fill((255,255,255,0))

        shape = []
        for y in xrange(self.main.cardtable.size[1]):
            row = []
            for x in xrange(self.main.cardtable.size[0]):
                row.append(not self.main.cardtable.check_if_legal_index((x,y),"pony"))
            shape.append(row)


        for x in xrange(self.main.cardtable.size[0]):
            for y in xrange(self.main.cardtable.size[1]):
                if (x+self.total_offset[0])%2 == (y+self.total_offset[1])%2:
                    color = (198,185,224,255)
                else:
                    color = (179,173,227,255)
                rect = (x*self.tile_size[0],y*self.tile_size[1],self.tile_size[0],self.tile_size[1])

                fill = False
                for X in xrange(-1,2):
                    for Y in xrange(-1,2):
                        pos = (x+X,y+Y)
                        if pos[0] >= 0 and pos[0] < self.main.cardtable.size[0] and pos[1] >= 0 and pos[1] < self.main.cardtable.size[0]:
                            if not self.main.cardtable.check_if_legal_index(pos,"pony"):
                                fill = True
                                break
                if not fill:
                    color = (255,255,255,0)

                self.rendered_surface.fill(color,rect)
        #renders the cards
        for child in self.children:
            child.render()


class XY_Range(object):
    def __init__(self):
        self.is_empty = True

    def extend(self,pos,size=(0,0)):
        if self.is_empty:
            self.min_x = pos[0]
            self.min_y = pos[1]
            self.max_x = pos[0]+size[0]
            self.max_y = pos[1]+size[1]
        else:
            self.min_x = min(pos[0],self.min_x)
            self.min_y = min(pos[1],self.min_y)
            self.max_x = max(pos[0]+size[0],self.max_x)
            self.max_y = max(pos[1]+size[1],self.max_y)
        self.is_empty = False


class CardTable(object):
    def __init__(self, size=(3,3)):
        self.size = size

        self.pony_cards = []
        for y in xrange(size[1]):
            row = []
            for x in xrange(size[0]):
                row.append(None)
            self.pony_cards.append(row)

        self.v_ship_cards = []
        for y in xrange(size[1]-1):
            row = []
            for x in xrange(size[0]):
                row.append(None)
            self.v_ship_cards.append(row)

        self.h_ship_cards = []
        for y in xrange(size[1]):
            row = []
            for x in xrange(size[0]-1):
                row.append(None)
            self.h_ship_cards.append(row)

    def refactor(self):
        #this function resizes and realligns everything
        xy = XY_Range()

        for y in xrange(self.size[1]):
            for x in xrange(self.size[0]):
                if self.pony_cards[y][x] != None:
                    xy.extend((x-1,y-1),(1,1))

        for y in xrange(self.size[1]-1):
            for x in xrange(self.size[0]):
                if self.v_ship_cards[y][x] != None:
                    xy.extend((x,y),(0,0))

        for y in xrange(self.size[1]):
            for x in xrange(self.size[0]-1):
                if self.h_ship_cards[y][x] != None:
                    xy.extend((x,y),(0,0))

        #now that we have our ranges, we need to make a new table
        if xy.is_empty:
            ct = CardTable()
            self.pony_cards = ct.pony_cards
            self.v_ship_cards = ct.v_ship_cards
            self.h_ship_cards = ct.h_ship_cards
        else:
            new_size = (max(xy.max_x-xy.min_x+2,3),max(xy.max_y-xy.min_y+2,3))
            ct = CardTable(new_size)

            for y in xrange(self.size[1]):
                for x in xrange(self.size[0]):
                    if ct.check_if_legal_index((x-xy.min_x,y-xy.min_y),"pony"):
                        ct.pony_cards[y-xy.min_y][x-xy.min_x] = self.pony_cards[y][x]

            for y in xrange(self.size[1]-1):
                for x in xrange(self.size[0]):
                    if ct.check_if_legal_index((x-xy.min_x,y-xy.min_y),"v ship"):
                        ct.v_ship_cards[y-xy.min_y][x-xy.min_x] = self.v_ship_cards[y][x]

            for y in xrange(self.size[1]):
                for x in xrange(self.size[0]-1):
                    if ct.check_if_legal_index((x-xy.min_x,y-xy.min_y),"h ship"):
                        ct.h_ship_cards[y-xy.min_y][x-xy.min_x] = self.h_ship_cards[y][x]

            self.pony_cards = ct.pony_cards
            self.v_ship_cards = ct.v_ship_cards
            self.h_ship_cards = ct.h_ship_cards

            self.size = new_size
        return xy

    def check_if_legal_index(self,index,type,replacable_cards = []):
        if type == "pony":
            return index[0] >= 0 and index[0] <= self.size[0]-1 and index[1] >= 0 and index[1] <= self.size[1]-1 and (self.pony_cards[index[1]][index[0]] in [None] + list(replacable_cards))
        elif type == "v ship":
            test1 = index[0] >= 0 and index[0] < self.size[0]-2 and index[1] >= 0 and index[1] < self.size[1]-1
            if test1:
                test2 = (self.v_ship_cards[index[1]][index[0]] in [None] + list(replacable_cards))
                return test2
            return False
        elif type == "h ship":
            test1 = index[0] >= 0 and index[0] < self.size[0]-1 and index[1] >= 0 and index[1] < self.size[1]-2
            if test1:
                test2 = (self.h_ship_cards[index[1]][index[0]] in [None] + list(replacable_cards))
                return test2
            return  False
        raise TypeError("This is not a legal type: "+type)


class Main(object):
    def __init__(self):
        self.screen_size = (1280,600)#(854,480)#(800,600)
        self.screen = pygame.display.set_mode(self.screen_size)

        self.bg_color = (127,127,127)

        self.framerate = 60
        self.clock = pygame.time.Clock()

        self.stills = []
        self.still_freq = 1/10.0
        self.last_still = time.time()-self.still_freq

        self.reset()
        self.run()

    def reset(self):
        self.controller = None #Controllers are used to control the application while something is being taken care of.

        self.maindeck = deck.MasterDeck()
        self.maindeck.load_all_cards()

        self.pony_deck = deck.Deck()
        self.ship_deck = deck.Deck()
        self.goal_deck = deck.Deck()

        self.cards_scaled_images = {}#keys are NAME, X%

        while True:
            c = self.maindeck.draw_card()
            if c == None: break
            elif c.type == "pony": self.pony_deck.add_card_to_bottom(c)
            elif c.type == "ship": self.ship_deck.add_card_to_bottom(c)
            elif c.type == "goal": self.goal_deck.add_card_to_bottom(c)
            else: raise TypeError("dafuq is this card's type?")

        self.pony_deck.shuffle()
        self.ship_deck.shuffle()
        self.goal_deck.shuffle()

        self.player_hand = deck.Deck()

        self.cardtable = CardTable()

        #puts the start card out
        c = None
        for card in self.pony_deck.cards:
            if card.name == "Fanfic Author Twilight":
                c = card
                break

        if c != None:
            self.pony_deck.remove_card(c)
            self.cardtable.pony_cards[1][1] = c

        self.hover_card = None
        self.flagged_for_rerender_hovercard = False

        self.selected_card_element = None
        self.card_to_be_placed_type = None
        self.card_to_be_placed_index = (0,0)

        #SETS UP THE GUI

        self.updated_elements = []

        self.main_element = Element(self,(0,0),self.screen_size,None,None,True)

        self.cardtable_gui = Element(self,(0,0),(self.screen_size[0]-200,self.screen_size[1]),self.main_element,(198-16,185-16,224-16))
        self.right_gui = RightGuiElement(self,(self.screen_size[0]-200,0),(200,self.screen_size[1]),self.main_element,(173,204,227))
        self.bottom_gui = PlayerHandElement(self,(0,self.screen_size[1]-125),(self.screen_size[0]-200,125),self.main_element,(197,96,204))

        self.cardtable_element = CardTableElement(self,(0,0),(0,0),self.cardtable_gui,always_count_hover=True)

        playerlist = Element(self,(0,0),(200,150),self.right_gui,(255,255,255))
        endturn_button = EndTurnButton(self,(0,0),(200,50),self.right_gui)
        decks_gui = Element(self,(0,0),(200,100),self.right_gui,(197,96,204))
        goalcards_scrollable = ScrollableGoalsGuiElement(self,(0,0),(200,300),self.right_gui,(173,204,227))

    def set_hover_card(self, card):
        self.hover_card = card
        self.flagged_for_rerender_hovercard = True

    def unset_hover_card(self, card):
        if card == self.hover_card:
            self.hover_card = None
            self.flagged_for_rerender_hovercard = True

    def update(self):
        for e in self.events:
            if e.type == MOUSEMOTION:
                self.main_element.update_for_mouse_move(e.pos)
                #if (self.keys[K_LALT] or self.keys[K_RALT]):
                #    self.flagged_for_rerender_hovercard = True
            elif e.type == MOUSEBUTTONDOWN:
                self.main_element.update_for_mouse_button_press(e.pos,e.button)
            elif e.type == MOUSEBUTTONUP:
                self.main_element.update_for_mouse_button_release(e.pos,e.button)

            elif e.type == KEYDOWN:
                if e.key == K_p:
                    #draws a pony card
                    c = self.pony_deck.draw_card()
                    if c != None: self.player_hand.add_card_to_bottom(c)
                    self.bottom_gui.update_hand()
                elif e.key == K_s:
                    #draws a ship card
                    c = self.ship_deck.draw_card()
                    if c != None: self.player_hand.add_card_to_bottom(c)
                    self.bottom_gui.update_hand()
                elif e.key == K_EQUALS:
                    self.cardtable_element.zoom_in()
                elif e.key == K_MINUS:
                    self.cardtable_element.zoom_out()

        for element in self.updated_elements:
            element.update()

        if self.controller != None:
            self.controller.update()

    def move(self):
        if self.controller != None:
            self.controller.move()

    def render(self):
        #self.screen.fill(self.bg_color)

        self.main_element.rendered_surface = self.screen
        for e in self.events:
            if e.type in (KEYDOWN,KEYUP) and e.key in (K_LALT,K_RALT):
                self.flagged_for_rerender_hovercard = True
                if e.type == KEYDOWN:
                    self.keys[e.key] = True
                else:
                    self.keys[e.key] = False
        if self.flagged_for_rerender_hovercard:
            self.main_element.flag_for_rerender()
        rerendered = bool(self.main_element.needs_to_rerender)
        self.main_element.render()

        if self.controller != None:
            self.controller.render()

        if rerendered and (self.keys[K_LALT] or self.keys[K_RALT]) and self.hover_card != None:
            #display the hover card
            dif = (self.screen_size[0]-CARDSIZE[0],self.screen_size[1]-CARDSIZE[1])
            if dif[0]<dif[1]:
                #This means that the width is the bigger one
                width = self.screen_size[0]
                height = CARDSIZE[1]*(width/float(CARDSIZE[0]))
            else:
                height = self.screen_size[1]
                width = CARDSIZE[0]*(height/float(CARDSIZE[1]))
            size = (int(width),int(height))
            img = pygame.transform.smoothscale(self.hover_card.image,size)
            if self.mouse_pos[0] < self.screen_size[0]/2:
                rect = img.get_rect( topright = (self.screen_size[0],0) )
            else:
                rect = img.get_rect( topleft = (0,0) )
            #self.screen.fill((127,127,127),None,special_flags = BLEND_RGB_MULT)
            self.screen.blit(img,rect)

        self.flagged_for_rerender_hovercard = False

        pygame.display.flip()

        """
        if self.time > self.last_still+self.still_freq:
            self.last_still = float(self.time)
            copy = self.screen.copy()
            temp = pygame.Surface((10,10))
            temp.fill((255,255,255))
            temp.blit(copy,(5-self.mouse_pos[0],5-self.mouse_pos[1]),special_flags = BLEND_RGB_SUB)
            copy.blit(temp,(self.mouse_pos[0]-5,self.mouse_pos[1]-5))
            self.stills.append(copy)
        """

    def run(self):
        self.running = True
        while self.running:
            self.time = time.time()
            self.keys = list(pygame.key.get_pressed())
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

        for i in xrange(len(self.stills)):
            pygame.image.save(self.stills[i], "stills/"+str(len(self.stills)-i)+".bmp")

        pygame.quit()


class Controller(object):
    def __init__(self,main):
        self.main = main

    def init(self):
        pass

    def update(self):
        pass

    def move(self):
        pass

    def cancel(self):
        self.main.controller = None

    def render(self):
        pass

class ControllerPlaceCard(Controller):
    #This controller is designed to control the application while the player selects where they'd like to place their card.
    def init(self):
        self.selected_card = self.main.bottom_gui.children_order[self.main.bottom_gui.selected_index].card

    def update(self):
        if self.main.cardtable_element.hover:
            #TODO: Find out where the card would be places given the current mouse position

            attempted_to_place_card = False
            for e in self.main.events:
                if e.type == MOUSEBUTTONDOWN and e.button == 1:
                    attempted_to_place_card = True

            if attempted_to_place_card:
                card = self.main.card_to_be_placed
                index = self.main.card_to_be_placed_index
                type = self.main.card_to_be_placed_type
                if type == "pony":
                    self.main.cardtable.pony_cards[index[1]][index[0]] = card
                elif type == "v ship":
                    self.main.cardtable.v_ship_cards[index[1]][index[0]] = card
                elif type == "h ship":
                    self.main.cardtable.h_ship_cards[index[1]][index[0]] = card
                else:
                    raise TypeError("Unknown type: "+type)
                offset = self.main.cardtable.refactor()
                self.main.card_to_be_placed = None
                self.main.card_to_be_placed_index = (0,0)
                self.main.card_to_be_placed_type = None
                self.set_zoom(self.zoom,force=True)
                if not offset.is_empty:
                    self.set_pos((self.pos[0]+(offset.min_x*self.tile_size[0]),self.pos[1]+(offset.min_y*self.tile_size[1])))
                self.total_offset[0] += offset.min_x
                self.total_offset[1] += offset.min_y
                self.main.player_hand.remove_card(card)
                self.main.bottom_gui.update_hand()

    def render(self):
        if self.main.cardtable_element.hover:
            card = self.selected_card
            #first we need to determine where the card would be located, which is based on it's type
            world_pos = self.main.cardtable_element.get_world_pos()
            pos = (int(world_pos[0]),int(world_pos[1]))
            pos = (self.main.mouse_pos[0]-pos[0],self.main.mouse_pos[1]-pos[1])

            img = None
            rect = None

            if card.type == "pony":
                index = (int(pos[0]/float(self.cardtable_element.tile_size[0])),int(pos[1]/float(self.cardtable_element.tile_size[1])))
                if self.cardtable.check_if_legal_index(index,"pony"):
                    img = pygame.transform.smoothscale(card.image, self.cardtable_element.card_size)
                    rect = img.get_rect( center = (world_pos[0] + (index[0]+0.5)*self.cardtable_element.tile_size[0],
                                                   world_pos[1] + (index[1]+0.5)*self.cardtable_element.tile_size[1]) )
                    self.card_to_be_placed_type = "pony"

            elif card.type == "ship":
                #This one is a bit trickier, since the card would go between the lines of the grid
                v_dif = min(pos[1]%self.cardtable_element.tile_size[1],(-pos[1])%self.cardtable_element.tile_size[1])
                h_dif = min(pos[0]%self.cardtable_element.tile_size[0],(-pos[0])%self.cardtable_element.tile_size[0])

                if v_dif < h_dif:
                    #This would be of type vertical
                    index = (floorint(pos[0]/float(self.cardtable_element.tile_size[0]))-1,floorint((pos[1]-(self.cardtable_element.tile_size[1]/2))/float(self.cardtable_element.tile_size[1])))
                    if self.cardtable.check_if_legal_index(index,"v ship"):
                        img = pygame.transform.smoothscale(card.image, self.cardtable_element.card_size)
                        rect = img.get_rect( center = (world_pos[0] + (index[0]+1.5)*self.cardtable_element.tile_size[0],
                                                       world_pos[1] + (index[1]+1.0)*self.cardtable_element.tile_size[1]) )
                        self.card_to_be_placed_type = "v ship"
                else:
                    #This would be of type horizontal
                    index = (floorint((pos[0]-(self.cardtable_element.tile_size[0]/2))/float(self.cardtable_element.tile_size[0])),floorint(pos[1]/float(self.cardtable_element.tile_size[1]))-1)
                    if self.cardtable.check_if_legal_index(index,"h ship"):
                        img = pygame.transform.rotate(pygame.transform.smoothscale(card.image, self.cardtable_element.card_size),90)
                        rect = img.get_rect( center = (world_pos[0] + (index[0]+1.0)*self.cardtable_element.tile_size[0],
                                                       world_pos[1] + (index[1]+1.5)*self.cardtable_element.tile_size[1]) )
                        self.card_to_be_placed_type = "h ship"

            if rect != None:
                self.card_to_be_placed_index = index
                alpha_array = pygame.surfarray.pixels_alpha(img)
                alpha_array /= 2
                del alpha_array
                self.screen.blit(img,rect)
            else:
                self.card_to_be_placed_type = None
                self.card_to_be_placed_index = (0,0)

main = Main()