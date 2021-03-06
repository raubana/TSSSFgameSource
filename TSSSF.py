import os
#os.environ['SDL_VIDEO_CENTERED'] = '1'

import pygame
from pygame.locals import *
pygame.mixer.pre_init(frequency=44100 ,buffer = 2**10)
pygame.init()

from libs.GUI.GUI import *
from libs.Deck import *
from libs.locals import *
from libs.CardTable import *

from libs.Controllers.StartUpController import *
from libs.Controllers.ConnectMenuController import *
from libs.Sprite.ChatSprite import ChatSprite

import math, random, time

print " --- TSSSFgame ---"
print "Created by Dylan J. Raub"
print "Original card-game by Horrible People Games"
print
print "Client:  Version "+CLIENT_VERSION
print " =================== "
print

class Main(object):
	def __init__(self):
		icon = pygame.image.load("imgs/window_icon.bmp")
		pygame.display.set_icon(icon)

		self.screen_size = (640, 480)
		self.screen = pygame.display.set_mode(self.screen_size, RESIZABLE)

		pygame.display.set_caption("TSSSF - Computer Game","TSSSF")

		pygame.scrap.init()

		self.framerate = 60
		self.clock = pygame.time.Clock()

		self.stills = []
		self.still_freq = 1 / 10.0
		self.last_still = time.time() - self.still_freq

		self.font = pygame.font.Font("data/fonts/Ubahn-Light.ttf",16)
		self.font_bold = pygame.font.Font("data/fonts/Ubahn-Light.ttf",14)
		self.font_bold.set_bold(True)
		self.timer_font = pygame.font.Font("data/fonts/Barth_Regular.ttf",24)
		self.deck_count_font = pygame.font.Font("data/fonts/PackardAntique-Bold.ttf",24)
		self.tiny_font = pygame.font.SysFont("Tahoma",9)

		self.sounds = {}

		self.sounds["connected"] = pygame.mixer.Sound("snds/app/connected.wav")
		self.sounds["lost_connection"] = pygame.mixer.Sound("snds/app/lost_connection.wav")

		self.sounds["game_timer"] = pygame.mixer.Sound("snds/game/misc/game_timer.wav")

		self.sounds["chat"] = pygame.mixer.Sound("snds/app/chat.wav")
		self.sounds["name_mentioned"] = pygame.mixer.Sound("snds/app/squee1.wav")
		self.sounds["player_ready"] = pygame.mixer.Sound("snds/app/player_ready.wav")
		self.sounds["player_not_ready"] = pygame.mixer.Sound("snds/app/player_not_ready.wav")

		self.sounds["add_card_to_deck"] = pygame.mixer.Sound("snds/card/add_card_to_deck.wav")
		self.sounds["add_card_to_hand"] = pygame.mixer.Sound("snds/card/add_card_to_hand.wav")
		self.sounds["add_card_to_table"] = pygame.mixer.Sound("snds/card/add_card_to_table.wav")
		self.sounds["draw_card_from_deck"] = pygame.mixer.Sound("snds/card/draw_card_from_deck.wav")
		self.sounds["draw_card_from_hand"] = pygame.mixer.Sound("snds/card/draw_card_from_hand.wav")
		self.sounds["draw_card_from_table"] = pygame.mixer.Sound("snds/card/draw_card_from_table.wav")
		self.sounds["place_deck"] = pygame.mixer.Sound("snds/card/place_deck.wav")
		self.sounds["remove_deck"] = pygame.mixer.Sound("snds/card/remove_deck.wav")
		self.sounds["shuffle_deck"] = pygame.mixer.Sound("snds/card/shuffle.wav")

		self.sounds["drink_call"] = pygame.mixer.Sound("snds/game/misc/drink_call.wav")
		self.sounds["players_turn"] = pygame.mixer.Sound("snds/app/players_turn_not_focused.wav")
		self.sounds["players_turn_not_focused"] = pygame.mixer.Sound("snds/app/players_turn_not_focused.wav")

		self.sounds["gender_swapped"] = pygame.mixer.Sound("snds/game/attribute_change/gender_swapped.wav")
		self.sounds["changed_race"] = pygame.mixer.Sound("snds/game/attribute_change/gender_swapped.wav")
		self.sounds["added_keyword"] = pygame.mixer.Sound("snds/game/attribute_change/gender_swapped.wav")
		self.sounds["imitate_card"] = pygame.mixer.Sound("snds/game/attribute_change/imitate_card.wav")

		self.sounds["won_goal"] = pygame.mixer.Sound("snds/game/misc/win_goal.wav")

		pygame.key.set_repeat(300, 30)

		# SETS UP THE GUI
		self.element_level = 0

		self.updated_elements = []
		self.elements_to_pack = {}

		self.needs_to_pack = False
		self.focus = None
		self.tooltip_text = None
		self.hover_focus_time = 0
		self.tooltip_surface = None

		self.main_element = Element(self, self, (0,0), self.screen_size, bg=(230,210,230))
		self.main_element.set_text_align(ALIGN_MIDDLE)

		self.client = None
		self.connecting = False
		self.server_is_pinged = False

		self.controller = StartUpController(self)  # Controllers are used to control the application while something is being taken care of.

		self.manage_pack_requests()

		self.my_master_deck = MasterDeck()

		self.setup_trayicon()

		self.blink_trayicon = False
		self.last_blinked_trayicon = 0
		self.last_trayicon = False

		self.reset()
		self.run()

	def setup_trayicon(self):
		#At the moment, this will only work for Window's users.
		try:
			from libs.TaskBarIcon import TaskBarIcon
			self.trayicon = TaskBarIcon()
		except:
			self.trayicon = None

	def play_sound(self, soundname, force=False):
		if soundname in self.sounds:
			if pygame.key.get_focused() or force:
				self.sounds[soundname].play()
		else:
			print "That sound doesn't appear to be in my list: '"+soundname+"'"

	def reset(self):
		#This function is used to clear out any game data that may remain from a previous game
		self.name = None
		self.master_deck = MasterDeck()
		self.card_table = CardTable()

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
				if DEBUG_MOUSEBUTTONPRESS_TRACE:
					print ""
				if e.button <= 3: self.mouse_button[e.button-1] = True
				self.main_element.update_for_mouse_button_press(e.pos, e.button)
			elif e.type == MOUSEBUTTONUP:
				if e.button <= 3: self.mouse_button[e.button-1] = False
				self.main_element.update_for_mouse_button_release(e.pos, e.button)
			elif e.type == KEYDOWN:
				self.keys[e.key] = True
				if self.focus != None:
					self.focus.update_for_keydown(e.unicode, e.key)
					if e.key == K_ESCAPE and self.client and self.focus == None:
						self.client.send("CANCEL_ACTION")
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

		if self.tooltip_text != None and self.tooltip_surface == None:
			if type(self.tooltip_text) in (unicode,str):
				if self.time - self.hover_focus_time >= 0.5:
					self.create_tooltip_surface()
			elif type(self.tooltip_text) == Card and (self.keys[K_LALT] or self.keys[K_RALT]):
				self.create_tooltip_surface()
		elif self.tooltip_surface != None:
			if type(self.tooltip_text) == Card:
				if not (self.keys[K_LALT] or self.keys[K_RALT]):
					self.tooltip_surface = None
					self.main_element.flag_for_rerender()
			elif self.tooltip_text == None:
				self.tooltip_surface = None
				self.main_element.flag_for_rerender()

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

		if self.blink_trayicon:
			if pygame.key.get_focused() or self.trayicon == None:
				self.blink_trayicon = False
				if self.trayicon != None:
					self.trayicon.set_icon(self.trayicon.default_icon)
			else:
				if self.time >= self.last_blinked_trayicon+0.75:
					self.last_blinked_trayicon = self.time
					self.last_trayicon = not self.last_trayicon
					if self.last_trayicon:
						icon = self.trayicon.attention_icon
					else:
						icon = self.trayicon.default_icon
					self.trayicon.set_icon(icon)

	def set_tooltip(self, text):
		if text != self.tooltip_text:
			if type(text) in (str,unicode):
				self.tooltip_text = str(text)
			elif type(text) == Card:
				self.tooltip_text = text
			else:
				self.tooltip_text = None
			self.hover_focus_time = float(self.time)
			self.tooltip_surface = None
			self.main_element.flag_for_rerender()

	def create_tooltip_surface(self):
		c1 = (255,255,196,192)
		c2 = (127,64,64)

		if type(self.tooltip_text) in (str,unicode):
			size = [0,0]
			lines = self.tooltip_text.split("\n")
			for line in lines:
				line_size = self.tiny_font.size(line)
				size[0] = max(size[0], line_size[0])
				size[1] = size[1]+line_size[1]
			size = (size[0]+3,size[1]+2)
			self.tooltip_surface = pygame.Surface(size,SRCALPHA)
			self.tooltip_surface.fill(c1)
			pygame.draw.rect(self.tooltip_surface,c2,(0,0,size[0],size[1]),1)
			for i in xrange(len(lines)):
				text_img = self.tiny_font.render(lines[i],True,c2)
				self.tooltip_surface.blit(text_img,(2,1+(i*self.tiny_font.get_height())))
		elif type(self.tooltip_text) == Card:
			size = (int((CARD_SIZE[0]*self.screen_size[1])/float(CARD_SIZE[1])),self.screen_size[1])
			if size[1] > CARD_SIZE[1]:
				size = list(CARD_SIZE)
			self.tooltip_surface = pygame.Surface(size,SRCALPHA)
			self.tooltip_surface.fill(c1)
			if size != CARD_SIZE:
				self.tooltip_surface.blit(pygame.transform.smoothscale(self.tooltip_text.get_image(), size), (0,0))
			else:
				self.tooltip_surface.blit(self.tooltip_text.get_image(), (0,0))
			pygame.draw.rect(self.tooltip_surface,c2,(0,0,size[0],size[1]),1)

		self.main_element.flag_for_rerender()

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
					if CLIENT_DEBUG_PRINT_STREAM:
						if message != "PING" and message != "PONG" and not message.startswith("CARDFILE:") and not message.startswith("CARDFILE_ATTRIBUTES:") and not message.startswith("TIMER:"):
							print "STARTSTREAM: "+message
							print ":ENDSTREAM"
					"""
					elif message.startswith("ADD_CHAT:"):
						chat = message[len("ADD_CHAT:"):]
						self.chat_sprites.append(ChatSprite(self,(0,0),(1,1),20))
						if chat.startswith("SERVER:"):
							chat = chat[len("SERVER:"):]
							self.chat_sprites[-1].set_text(chat,(64,0,64,255),(255,127,255,127))
						elif chat.startswith("PLAYER:"):
							chat = chat[len("PLAYER:"):]
							i = chat.find(":")
							if i != -1:
								name = chat[:i]
								msg = chat[i+1:]
							else:
								name = "?"
								msg = chat
							msg = msg.strip()
							if msg.startswith("/me "):
								msg = msg[len("/me "):]
								self.chat_sprites[-1].set_text(name+" "+msg,(64,64,64,255))
							elif msg.startswith(">"):
								msg = msg[len(">"):]
								self.chat_sprites[-1].set_text("> "+name+": "+msg,(0,96,0,255))
							else:
								self.chat_sprites[-1].set_text(chat)
							self.play_sound("chat")
						else:
							self.chat_sprites[-1].set_text(chat)
						self.main_element.flag_for_rerender()
					"""
					if message == PING_MESSAGE:
						self.client.send(PONG_MESSAGE)
					elif message == PONG_MESSAGE:
						pass
					elif message.startswith("ALERT:"):
						sound_name = message[len("ALERT:"):]
						self.play_sound(sound_name)
					elif message.startswith("KICK:"):
						chat = message[len("KICK:"):]
						self.client.close()
						self.client = None
						self.play_sound("lost_connection")
						self.controller = ConnectMenuController(self)
						self.controller.message_element.set_text(chat)
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

				#we try to get the user's attention.
				if self.trayicon != None and not pygame.key.get_focused():
					self.trayicon.ShowBalloon("Whoops","You've lost connection.", 15*1000)

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
		if rerender: self.controller.rerender = True

		#Main Element (the GUI)
		self.main_element.render()

		#Controller
		if self.controller != None:
			self.controller.render()

		#Chat
		if rerender:
			for s in self.chat_sprites:
				s.render()

		#Tooltip
		if rerender and self.tooltip_surface != None:
			pos = [self.mouse_pos[0]+10, self.mouse_pos[1]+10]
			size = self.tooltip_surface.get_size()
			if size[0] > self.screen_size[0]:
				pos[0] = 0
			elif pos[0] + size[0] > self.screen_size[0]:
				pos[0] = self.screen_size[0] - size[0]
			if size[1] > self.screen_size[1]:
				pos[1] = 0
			elif pos[1] + size[1] > self.screen_size[1]:
				pos[1] = self.screen_size[1] - size[1]
			self.screen.blit(self.tooltip_surface, pos)

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

			if self.controller != None and not self.controller.disable_framerate:
				self.clock.tick(self.framerate)

		for i in xrange(len(self.stills)):
			pygame.image.save(self.stills[i], "stills/" + str(len(self.stills) - i) + ".bmp")
		if self.client != None:
			self.client.close()
		print "GOODBYE!!"
		pygame.quit()
		if self.trayicon != None:
			self.trayicon.Destroy()



#try:
main = Main()
"""
except Exception, e:
	pygame.quit()
	print traceback.format_exc()
	input("Press enter to quit.")
"""
