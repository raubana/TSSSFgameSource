import pygame
from pygame.locals import *
pygame.mixer.pre_init(buffer = 2**9)
pygame.init()

#import numpy

import math, random, time

from libs.GUI.GUI import *
from libs.Deck import *
from libs.locals import *

from libs.Controllers.ConnectMenuController import *
from libs.Sprite.ChatSprite import ChatSprite

class Main(object):
	def __init__(self):
		self.screen_size = (854, 480)
		self.screen = pygame.display.set_mode(self.screen_size, RESIZABLE)

		pygame.scrap.init()

		self.framerate = 60
		self.clock = pygame.time.Clock()

		self.stills = []
		self.still_freq = 1 / 10.0
		self.last_still = time.time() - self.still_freq

		self.font = pygame.font.SysFont("Tahoma",12)

		self.sounds = {}

		self.sounds["connected"] = pygame.mixer.Sound("snds/app/connected.ogg")
		self.sounds["lost_connection"] = pygame.mixer.Sound("snds/app/lost_connection.ogg")

		self.sounds["game_timer"] = pygame.mixer.Sound("snds/game/misc/game_timer.ogg")

		self.sounds["chat"] = pygame.mixer.Sound("snds/app/chat.ogg")
		self.sounds["player_ready"] = pygame.mixer.Sound("snds/app/player_ready.ogg")
		self.sounds["player_not_ready"] = pygame.mixer.Sound("snds/app/player_not_ready.ogg")

		self.sounds["add_card_to_deck"] = pygame.mixer.Sound("snds/card/add_card_to_deck.ogg")
		self.sounds["add_card_to_hand"] = pygame.mixer.Sound("snds/card/add_card_to_hand.ogg")
		self.sounds["add_card_to_table"] = pygame.mixer.Sound("snds/card/add_card_to_table.ogg")
		self.sounds["draw_card_from_deck"] = pygame.mixer.Sound("snds/card/draw_card_from_deck.ogg")
		self.sounds["draw_card_from_hand"] = pygame.mixer.Sound("snds/card/draw_card_from_hand.ogg")
		self.sounds["draw_card_from_table"] = pygame.mixer.Sound("snds/card/draw_card_from_table.ogg")
		self.sounds["place_deck"] = pygame.mixer.Sound("snds/card/place_deck.ogg")
		self.sounds["remove_deck"] = pygame.mixer.Sound("snds/card/remove_deck.ogg")
		self.sounds["shuffle_deck"] = pygame.mixer.Sound("snds/card/shuffle.ogg")

		pygame.key.set_repeat(300, 30)

		# SETS UP THE GUI
		self.element_level = 0

		self.updated_elements = []
		self.elements_to_pack = {}

		self.needs_to_pack = False
		self.focus = None
		self.main_element = Element(self, self, (0,0), self.screen_size, bg_color=(210,180,220))
		self.main_element.set_text_align(ALIGN_MIDDLE)

		self.client = None
		self.connecting = False
		self.server_is_pinged = False

		self.controller = ConnectMenuController(self)  # Controllers are used to control the application while something is being taken care of.

		self.manage_pack_requests()

		self.reset()
		self.run()

	def play_sound(self, soundname):
		if soundname in self.sounds:
			self.sounds[soundname].play()
		else:
			print "That sound doesn't appear to be in my list: '"+soundname+"'"

	def reset(self):
		#This function is used to clear out any game data that may remain from a previous game
		self.name = None
		self.master_deck = MasterDeck()

		self.chat_sprites = []

	def _setup_for_pack(self):
		# THIS SHOULD NOT BE CALLED UNLESS YOU KNOW WHAT YOU'RE DOING!!
		if self.needs_to_pack == False:
			self.needs_to_pack = True
			level_name = str(self.element_level)
			if level_name not in self.elements_to_pack:
				level = []
				self.elements_to_pack[level_name] = level
			else:
				level = self.elements_to_pack[level_name]
			level.append(self)

	def manage_pack_requests(self):
		# managed elements needing to be packed
		while len(self.elements_to_pack) > 0:
			#first we find the highest level needed to be packed
			keys = self.elements_to_pack.keys()
			highest = int(keys[0])
			for key in keys[1:]:
				highest = min(highest, int(key))
			#next, we make each element in that level pack
			elements_to_pack = self.elements_to_pack.pop(str(highest))
			for element in elements_to_pack:
				element.pack()

	def update(self):
		for e in self.events:
			if e.type == MOUSEMOTION:
				self.mouse_pos = e.pos
				self.main_element.update_for_mouse_move(e.pos)
			elif e.type == MOUSEBUTTONDOWN:
				if e.button <= 3: self.mouse_button[e.button-1] = True
				self.main_element.update_for_mouse_button_press(e.pos, e.button)
			elif e.type == MOUSEBUTTONUP:
				if e.button <= 3: self.mouse_button[e.button-1] = False
				self.main_element.update_for_mouse_button_release(e.pos, e.button)

			elif e.type == KEYDOWN:
				self.keys[e.key] = True
				if self.focus != None:
					self.focus.update_for_keydown(e.unicode, e.key)
				if self.focus == None or self.focus == self.main_element:
					message = None
					if e.key == K_1: message = "sound_add_card_to_deck"
					if e.key == K_2: message = "sound_add_card_to_hand"
					if e.key == K_3: message = "sound_add_card_to_table"
					if e.key == K_4: message = "sound_draw_card_from_deck"
					if e.key == K_5: message = "sound_draw_card_from_hand"
					if e.key == K_6: message = "sound_draw_card_from_table"
					if e.key == K_7: message = "sound_place_deck"
					if e.key == K_8: message = "sound_remove_deck"
					if e.key == K_9: message = "sound_shuffle_deck"
					if message != None:
						self.chat_sprites.append(ChatSprite(self,(0,0),(1,1),3))
						self.chat_sprites[-1].set_text("playing "+message,(255,255,255,255),(0,0,0,255))
						self.play_sound(message)
						self.main_element.flag_for_rerender()
			elif e.type == KEYUP:
				self.keys[e.key] = False
				if self.focus != None:
					self.focus.update_for_keyup(e.key)

			elif e.type == VIDEORESIZE:
				self.screen_size = e.size
				self.screen = pygame.display.set_mode(self.screen_size, RESIZABLE)
				self.main_element.flag_for_rerender()
				self.main_element.flag_for_pack()

		for element in self.updated_elements:
			element.update()

		self.ping_server()
		self.read_messages()

		if self.controller != None:
			self.controller.update()

		i = len(self.chat_sprites) - 1
		while i >= 0:
			s = self.chat_sprites[i]
			s.update()
			if s.dead:
				self.chat_sprites.pop(i)
				self.main_element.flag_for_rerender()
			i -= 1

	def move(self):
		if self.controller != None:
			self.controller.move()

		y_pos = self.screen_size[1]
		i = len(self.chat_sprites) - 1
		while i >= 0:
			s = self.chat_sprites[i]
			y_pos -= s.size[1]
			s.pos = (0,int(y_pos))
			i -= 1

	def ping_server(self):
		#Ping
		if self.client != None and not self.connecting:
			if self.client.connected:
				lgm = self.client.server_last_got_message
				dif = self.time - lgm
				if dif >= PING_FREQUENCY:
					if not self.server_is_pinged:
						self.server_is_pinged = True
						self.client.send(PING_MESSAGE)
					else:
						# This means the server was already sent a 'ping', and we're waiting for a 'pong'
						if dif >= PING_FREQUENCY + TIMEOUT_TIME:
							#This server has timed out, so we must disconnect
							print "= Server has timed-out."
							self.client.close()
				else:
					self.server_is_pinged = False

	def read_messages(self):
		if self.client != None:
			if self.client.connected:
				if len(self.client.received_messages) > 0:
					message = self.client.received_messages.pop(0)
					if message == PING_MESSAGE:
						self.client.send(PONG_MESSAGE)
					elif message == PONG_MESSAGE:
						pass
					elif message.startswith("ADD_CHAT:"):
						chat = message[len("ADD_CHAT:"):]
						self.chat_sprites.append(ChatSprite(self,(0,0),(1,1),20))
						if chat.startswith("SERVER:"):
							chat = chat[len("SERVER:"):]
							self.chat_sprites[-1].set_text(chat,(64,0,64,255),(255,127,255,127))
						elif chat.startswith("PLAYER:"):
							chat = chat[len("PLAYER:"):]
							self.play_sound("chat")
							self.chat_sprites[-1].set_text(chat)
						else:
							self.chat_sprites[-1].set_text(chat)
						self.main_element.flag_for_rerender()
					elif message.startswith("ALERT:"):
						sound_name = message[len("ALERT:"):]
						self.play_sound(sound_name)
					else:
						attempt = self.controller.read_message(message)
						if not attempt:
							print "ERROR! Retrieved message unreadable:"+message
			elif not self.connecting:
				self.client.close()
				self.client = None
				self.play_sound("lost_connection")
				self.controller = ConnectMenuController(self)
				self.controller.message_element.set_text("Lost Connection")

	def pack(self):
		if self.needs_to_pack:
			self.needs_to_pack = False

			new_pos = (0, 0)
			new_size = self.screen_size
			redo = False
			if new_pos != self.main_element.pos:
				redo = True
				self.main_element.pos = new_pos
			if new_size != self.main_element.size:
				redo = True
				self.main_element.size = new_size
				self.main_element._setup_for_pack()
			if redo:
				self.main_element.update_rect()
				self.main_element.flag_for_rerender()

	def render(self):
		rerender = self.main_element.needs_to_rerender or (self.controller != None and self.controller.rerender)
		self.main_element.render()

		if self.controller != None:
			self.controller.render()

		if rerender:
			for s in self.chat_sprites:
				s.render()

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
			self.mouse_pos = list(pygame.mouse.get_pos())
			self.mouse_button = list(pygame.mouse.get_pressed())
			self.events = pygame.event.get()

			self.update()
			self.manage_pack_requests()
			self.move()
			self.manage_pack_requests()
			self.render()

			for e in self.events:
				if e.type == QUIT:
					print "Normal quit."
					self.running = False

			self.clock.tick(self.framerate)

		for i in xrange(len(self.stills)):
			pygame.image.save(self.stills[i], "stills/" + str(len(self.stills) - i) + ".bmp")
		if self.client != None:
			self.client.close()
		print "GOODBYE!!"
		pygame.quit()


main = Main()