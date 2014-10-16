from Controller import*

from ..GUI.GUI import *
from ..GUI.DeckElement import *
from ..GUI.CardElement import *
from ..GUI.TimerElement import *
from ..GUI.TableElement import *

import string, os

class GameController(Controller):
	def init(self):
		self.main.client.throttled = True

		#Clear the gui
		self.main.updated_elements = []
		self.main.main_element.clear()
		self.main.main_element.set_text("")
		#sets up main GUI
		self.main.main_element.layout = LAYOUT_SPLIT

		self.left_element = None#Element(self.main, self.main.main_element, None, (0,"100%"))
		self.main.main_element.children.append(None)
		self.top_element = Element(self.main, self.main.main_element, None, ("100%",50))
		self.right_element = Element(self.main, self.main.main_element, None, (150,"100%"))
		self.bottom_element = Element(self.main, self.main.main_element, None, ("100%",100))
		self.table_element = TableElement(self.main, self.main.main_element, None, ("100%","100%"))

		self.top_element.add_handler_keydown(self)
		self.right_element.add_handler_keydown(self)
		self.bottom_element.add_handler_keydown(self)
		self.table_element.add_handler_keydown(self)

		self.top_element.set_bg((175,125,175))
		self.right_element.set_bg(None)
		self.bottom_element.set_bg((175,125,175))
		self.table_element.set_bg((182,169,208))

		self.right_element.layout = LAYOUT_VERTICAL
		self.top_element.layout = LAYOUT_HORIZONTAL
		self.bottom_element.layout = LAYOUT_HORIZONTAL

		self.top_element.h_scrollable = True
		self.top_element.always_show_h_scroll = True
		self.bottom_element.h_scrollable = True
		self.bottom_element.always_show_h_scroll = True
		self.table_element.h_scrollable = True
		self.table_element.v_scrollable = True
		self.table_element.always_show_v_scroll = True
		self.table_element.always_show_h_scroll = True
		self.table_element.allow_rightclick_multi_axis_scrolling = True
		self.table_element.force_fullrange_scrolling = True

		self.player_list_element = Element(self.main, self.right_element, None, ("100%",50))
		self.timer_element = TimerElement(self.main, self.right_element, None, ("100%", int(self.main.timer_font.get_height()*1.2)))
		self.decks_element = Element(self.main, self.right_element, None, ("100%",75))
		self.public_goals_element = Element(self.main, self.right_element, None, ("100%","100%"))

		self.player_list_element.add_handler_keydown(self)
		self.decks_element.add_handler_keydown(self)
		self.public_goals_element.add_handler_keydown(self)

		self.timer_element.add_handler_mousepress(self)

		self.timer_element.set_text_color((255,255,255))

		self.timer_element.font = self.main.timer_font

		self.timer_element.set_text_align(ALIGN_MIDDLE)

		self.timer_element.set_bg((175,125,175))
		self.decks_element.set_bg((175,125,175))
		self.public_goals_element.set_bg((173,204,227))

		self.player_list_element.layout = LAYOUT_VERTICAL
		self.public_goals_element.layout = LAYOUT_VERTICAL

		self.public_goals_element.v_scrollable = True
		self.public_goals_element.always_show_v_scroll = True

		self.timer_element.menu_info.append(("End Turn", self.end_turn))

		self.pony_deck_wrapper_element = Element(self.main, self.decks_element, None, ("33%","50%"), bg=None)
		self.ship_deck_wrapper_element = Element(self.main, self.decks_element, None, ("50%","50%"), bg=None)
		self.goal_deck_wrapper_element = Element(self.main, self.decks_element, None, ("100%","50%"), bg=None)
		self.pony_discard_wrapper_element = Element(self.main, self.decks_element, None, ("33%","100%"), bg=None)
		self.ship_discard_wrapper_element = Element(self.main, self.decks_element, None, ("50%","100%"), bg=None)

		self.pony_deck_element = DeckElement(self.main, self.pony_deck_wrapper_element, None, ("50%","100%"),
										 	bg=ScaleImage(pygame.image.load("imgs/cardbacks/cardback_pony.png")))
		self.pony_deck_count_element = Element(self.main, self.pony_deck_wrapper_element, None, ("100%","100%"),
											bg=None, text_color=(255,255,255))
		self.ship_deck_element = DeckElement(self.main, self.ship_deck_wrapper_element, None, ("50%","100%"),
										 	bg=ScaleImage(pygame.image.load("imgs/cardbacks/cardback_ship.png")))
		self.ship_deck_count_element = Element(self.main, self.ship_deck_wrapper_element, None, ("100%","100%"),
											bg=None, text_color=(255,255,255))
		self.goal_deck_element = DeckElement(self.main, self.goal_deck_wrapper_element, None, ("50%","100%"),
										 	bg=ScaleImage(pygame.image.load("imgs/cardbacks/cardback_goal.png")))
		self.goal_deck_count_element = Element(self.main, self.goal_deck_wrapper_element, None, ("100%","100%"),
											bg=None, text_color=(255,255,255))
		self.pony_discard_element = DeckElement(self.main, self.pony_discard_wrapper_element, None, ("50%","100%"),
											bg=(255,255,255))
		self.pony_discard_count_element = Element(self.main, self.pony_discard_wrapper_element, None, ("100%","100%"),
											bg=None, text_color=(255,255,0))
		self.ship_discard_element = DeckElement(self.main, self.ship_discard_wrapper_element, None, ("50%","100%"),
											bg=(255,255,255))
		self.ship_discard_count_element = Element(self.main, self.ship_discard_wrapper_element, None, ("100%","100%"),
											bg=None, text_color=(255,255,0))

		self.pony_deck_count_element.font = self.main.deck_count_font
		self.ship_deck_count_element.font = self.main.deck_count_font
		self.goal_deck_count_element.font = self.main.deck_count_font
		self.pony_discard_count_element.font = self.main.deck_count_font
		self.ship_discard_count_element.font = self.main.deck_count_font

		self.pony_deck_count_element.set_text_align(ALIGN_MIDDLE)
		self.ship_deck_count_element.set_text_align(ALIGN_MIDDLE)
		self.goal_deck_count_element.set_text_align(ALIGN_MIDDLE)
		self.pony_discard_count_element.set_text_align(ALIGN_MIDDLE)
		self.ship_discard_count_element.set_text_align(ALIGN_MIDDLE)

		self.pony_deck_count_element.set_text("0")
		self.ship_deck_count_element.set_text("0")
		self.goal_deck_count_element.set_text("0")
		self.pony_discard_count_element.set_text("0")
		self.ship_discard_count_element.set_text("0")

		self.pony_deck_element.padding = (2,2,2,2)
		self.ship_deck_element.padding = (2,2,2,2)
		self.goal_deck_element.padding = (2,2,2,2)
		self.pony_discard_element.padding = (2,2,2,2)
		self.ship_discard_element.padding = (2,2,2,2)

		self.pony_deck_element.menu_info.append(("Draw 1",self.do_nothing))
		self.pony_deck_element.menu_info.append(("Shuffle",self.do_nothing))

		self.ship_deck_element.menu_info.append(("Draw 1",self.do_nothing))
		self.ship_deck_element.menu_info.append(("Shuffle",self.do_nothing))

		self.goal_deck_element.menu_info.append(("Shuffle",self.do_nothing))

		self.pony_discard_element.menu_info.append(("Draw Top",self.do_nothing))
		self.pony_discard_element.menu_info.append(("Draw...",self.do_nothing))
		self.pony_discard_element.menu_info.append(("Shuffle",self.do_nothing))
		self.pony_discard_element.menu_info.append(("Swap Decks",self.do_nothing))

		self.ship_discard_element.menu_info.append(("Draw Top",self.do_nothing))
		self.ship_discard_element.menu_info.append(("Draw...",self.do_nothing))
		self.ship_discard_element.menu_info.append(("Shuffle",self.do_nothing))
		self.ship_discard_element.menu_info.append(("Swap Decks",self.do_nothing))

		self.chat_input_element = None

		self.bottom_element.give_focus()

	def do_nothing(self):
		pass

	def end_turn(self):
		self.main.client.send("END_TURN")

	def play_card(self, args):
		self.main.client.send("PLAY_CARD:"+str(args[0]))

	def read_message(self, message):
		if message.startswith("PLAYERLIST:"):
			playerlist = message[len("PLAYERLIST:"):].split(",")
			self.player_list_element.clear()
			self.player_list_element.set_size(("100%",len(playerlist)*self.main.font.get_height()))
			for player in playerlist:
				parts = player.split(":")
				name = parts.pop()
				color = (0,0,0)
				bg_color = None
				if "L" in parts:
					color = (96,96,96)
				else:
					if "R" in parts:
						color = (0,127,0)
					elif "NR" in parts:
						color = (127,0,0)
				if "DC" in parts:
					bg_color = (192,192,192)
				if "CT" in parts:
					name = ">"+name
				else:
					name = " "+name
				element = Element(self.main,self.player_list_element,None,("100%",self.main.font.get_height()),bg_color,color)
				element.set_text(name)
				if "YOU" in parts:
					element.font = self.main.font_bold
		elif message.startswith("PLAYERHAND:"):
			print message
			s = message[len("PLAYERHAND:"):]
			self.bottom_element.clear()
			self.bottom_element.layout = LAYOUT_HORIZONTAL
			if len(s) > 0:
				hand = s.split(",")
				scale = 0.325
				size = (int(CARD_SIZE[0]*scale),int(CARD_SIZE[1]*scale))
				for x in xrange(len(hand)):
					s = hand[len(hand)-x-1]
					i = int(s)
					card = self.main.master_deck.cards[i]
					element = CardElement(self.main,self.bottom_element,None,size)
					element.set_card(card)
					element.padding = (3,3,3,3)
					if card.type == "pony":
						element.menu_info = [("Play Card", self.play_card, tuple([i])),
											 ("Action: Replace", self.do_nothing),
											 ("Discard", self.do_nothing)]
					elif card.type == "ship":
						element.menu_info = [("Play Card", self.play_card, tuple([i])),
											 ("Discard", self.do_nothing)]
		elif message.startswith("PUBLICGOALS:"):
			hand = message[len("PUBLICGOALS:"):].split(",")
			self.public_goals_element.clear()
			self.public_goals_element.layout = LAYOUT_VERTICAL
			scale = 0.4
			size = (int(CARD_SIZE[0]*scale),int(CARD_SIZE[1]*scale))
			for x in xrange(len(hand)):
				s = hand[len(hand)-x-1]
				i = int(s)
				card = self.main.master_deck.cards[i]
				element = CardElement(self.main,self.public_goals_element,None,size)
				element.set_card(card)
				element.padding = (3,3,3,3)
				element.menu_info = [("Win Goal", self.do_nothing),
									 ("Action: New Goal", self.do_nothing)]
		elif message.startswith("CARDTABLE:"):
			s = message[len("CARDTABLE:"):]
			self.main.card_table.parse_message(self.main.master_deck, s)
			self.table_element.setup_grid()
		elif message.startswith("TIMER:"):
			s = message[len("TIMER:"):]
			self.timer_element.set_text(s)
		elif message == "YOUR_TURN":
			if not pygame.key.get_focused():
				self.main.play_sound("players_turn_not_focused", True)
				#we try to get the user's attention.
				if self.main.trayicon != None:
					self.main.trayicon.ShowBalloon("Yay!","It's your turn!", 15*1000)
			else:
				self.main.play_sound("players_turn")
		elif message == "TURN_ALMOST_OVER":
			if not pygame.key.get_focused():
				self.main.play_sound("players_turn_not_focused", True)
				#we try to get the user's attention.
				if self.main.trayicon != None:
					self.main.trayicon.ShowBalloon("Uh oh!","You're almost out of time!", 15*1000)
			else:
				self.main.play_sound("players_turn")
		else:
			return False
		return True

	def handle_event_keydown(self, widget, unicode, key):
		if key == K_RETURN:
			self.chat_input_element = InputBox(self.main, self.main.main_element, (25,25), ("100%-50px",self.main.font.get_height()+2))
			self.chat_input_element.max_characters = 100
			self.chat_input_element.add_handler_submit(self)
			self.chat_input_element.add_handler_losefocus(self)
			self.chat_input_element.give_focus()

	def handle_event_submit(self, widget):
		if (not (self.chat_input_element == None)) and widget == self.chat_input_element:
			message = self.chat_input_element.text.strip()
			if len(message) > 0:
				if message == "!ready":
					self.main.client.send("READY")
				else:
					self.main.client.send("CHAT:"+self.chat_input_element.text)
			self.bottom_element.give_focus()

	def handle_event_losefocus(self, widget):
		if (not (self.chat_input_element == None)) and widget == self.chat_input_element:
			self.main.main_element._remove_child(self.chat_input_element)
			self.chat_input_element = None