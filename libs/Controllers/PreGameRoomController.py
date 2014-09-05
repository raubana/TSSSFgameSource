#!/usr/bin/env python
# -*- coding: utf-8 -*-

from Controller import*

from ..GUI.GUI import *
from ..netcom import Client

import string, os, thread

class PreGameRoomController(Controller):
	def init(self):
		self.players = None
		self.players_ready = None

		#Clear the gui
		self.main.updated_elements = []
		self.main.main_element.clear()
		self.main.main_element.set_text("")

		H = "100%-"+str(self.main.font.get_height()*4)+"px"

		self.chat_window = Element(self.main,
								   self.main.main_element,
								   None,
								   ("100%-"+str(self.main.font.size("0"*(PLAYERNAME_MAX_LENGTH+5))[0])+"px",H),
								   bg_color=(255,255,255))
		self.chat_window.layout = LAYOUT_VERTICAL
		self.chat_window.padding = [5,5,5,5]
		self.chat_window.h_scrollable = True
		#self.chat_window.always_show_h_scroll = True
		self.chat_window.v_scrollable = True
		#self.chat_window.always_show_v_scroll = True

		self.max_chat_lines = 50
		self.chat_line_elements = []
		self.chat_log = []

		self.playerlist_window = Element(self.main, self.main.main_element, None, ("100%",H), bg_color=(255,255,255))
		self.playerlist_window.padding = [0,5,5,5]

		self.text_inputbox = InputBox(self.main, self.main.main_element, None, ("100%",self.main.font.get_height()+4))
		self.text_inputbox.padding = [5,0,5,0]
		self.text_inputbox.max_characters = 100

		self.ready_button = Button(self.main,
								   self.main.main_element,
								   None,
								   (self.main.font.size("READY")[0]+15,self.main.font.get_height()+15))
		self.ready_button.margin = [5,5,5,5]
		self.ready_button.set_text("READY")

		self.move_scrollbar_down = True

		#custom resources
		self.symbols_font = pygame.font.SysFont("Wingdings", 12)

		self.sound_ready = pygame.mixer.Sound("snds/app/player_ready.ogg")
		self.sound_not_ready = pygame.mixer.Sound("snds/app/player_not_ready.ogg")

		#Sets up the handlers
		self.text_inputbox.add_handler_submit(self)
		self.ready_button.add_handler_submit(self)

		self.server_is_pinged = False

	def update(self):
		#Ping
		if self.main.client.connected:
			lgm = self.main.client.server_last_got_message
			dif = self.main.time - lgm
			if dif >= PING_FREQUENCY:
				if not self.server_is_pinged:
					self.server_is_pinged = True
					self.main.client.send(PING_MESSAGE)
				else:
					# This means the server was already sent a 'ping', and we're waiting for a 'pong'
					if dif >= PING_FREQUENCY + TIMEOUT_TIME:
						#This server has timed out, so we must disconnect
						print "= Server has timed-out."
						self.main.client.close()
			else:
				self.server_is_pinged = False
		#Everything else
		if self.main.client.connected:
			if len(self.main.client.received_messages) > 0:
				message = self.main.client.received_messages.pop(0)
				if message == PING_MESSAGE:
					self.main.client.send(PONG_MESSAGE)
				elif message.startswith("ADD_CHAT:"):
					chat = message[len("ADD_CHAT:"):]
					self.add_chat(chat)
				elif message.startswith("PLAYERLIST:"):
					s = message[len("PLAYERLIST:"):]
					self.players = s.split(",")
					self.players_ready = None
					self.update_players_list_window()
				elif message.startswith("PLAYERS_READY:"):
					s = message[len("PLAYERS_READY:"):]
					self.players_ready = s.split(",")
					self.update_players_list_window()
				elif message == "ALERT_READY":
					self.sound_ready.play()
				elif message == "ALERT_NOT_READY":
					self.sound_not_ready.play()
				elif message == "ALERT_TIMER":
					self.main.sound_game_timer.play()
				elif message == "BEGIN_LOAD":
					import GameStartingController
					self.main.controller = GameStartingController.GameStartingController(self.main)
		else:
			self.main.client.close()
			self.main.client = None
			import ConnectMenuController
			self.main.sound_lost_connection.play()
			self.main.controller = ConnectMenuController.ConnectMenuController(self.main)
			self.main.controller.message_element.set_text("Lost Connection")

		if self.chat_window.v_scrollbar != None:
			if self not in self.chat_window.v_scrollbar.scroll_handlers:
				self.chat_window.v_scrollbar.add_handler_scroll(self)

		if self.move_scrollbar_down:
			if self.chat_window.v_scrollbar != None and not self.chat_window.v_scrollbar.grabbed:
				self.chat_window.v_scrollbar.set_scrolled_amount(self.chat_window.v_scrollbar.max_scroll)

	def update_players_list_window(self):
		self.playerlist_window.clear()
		if len(self.players) > 0:
			i = 0
			while i < len(self.players):
				ready = None
				if self.players_ready != None:
					if self.players_ready[i] == "1":
						ready = True
					elif self.players_ready[i] == "0":
						ready = False
				if ready or not ready:
					if ready:
						ch = u""
						color = (0,127,0)
					else:
						ch = u""
						color = (196,127,127)
					element1 = Element(self.main, self.playerlist_window, None,
									   (int(self.symbols_font.size(ch)[0]),self.main.font.get_height()),
									   bg_color=None, text_color=color)
					element1.font = self.symbols_font
					element1.set_text(ch)
					element1.set_text_align(ALIGN_MIDDLE)
				element2 = Element(self.main, self.playerlist_window, None,
								   ("100%",self.main.font.get_height()), bg_color=None)
				element2.set_text(self.players[i])
				element2.set_text_align(ALIGN_MIDDLE)
				i += 1

	def handle_event_scroll(self, widget, amount):
		self.move_scrollbar_down = amount >= widget.max_scroll

	def add_chat(self, message):
		if message.startswith("PLAYER:"):
			self.main.sound_chat.play()
		self.chat_log.append(message)
		if len(self.chat_log) > self.max_chat_lines:
			self.chat_log.pop(0)
			self.chat_window._remove_child(self.chat_line_elements.pop(0))
		element = Element(self.main, self.chat_window, None, (0,0), bg_color=None)
		self.chat_line_elements.append(element)
		self.apply_message_to_element(message,element)

	def apply_message_to_element(self, message, element):
		if message.startswith("PLAYER:"):
			chat = message[len("PLAYER:"):]
			color = (0,0,0)
		elif message.startswith("SERVER:"):
			chat = message[len("SERVER:"):]
			color = (127,127,127)
		else:
			chat = message
			color = (127,0,0)
		element.set_size(self.main.font.size(chat))
		element.set_text(chat)
		element.set_text_color(color)

	def handle_event_submit(self, widget):
		if widget == self.text_inputbox:
			message = self.text_inputbox.text
			if message:
				self.main.client.send("CHAT:"+message)

				self.text_inputbox.set_text("")
				self.text_inputbox.index = 0
				self.text_inputbox.offset = 0
		elif widget == self.ready_button:
			self.main.client.send("READY")
