from Controller import*

from ..GUI.GUI import *
from ..GUI.DeckElement import *
from ..GUI.CardElement import *

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
		self.table_element = Element(self.main, self.main.main_element, None, ("100%","100%"))

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

		self.player_list_element = Element(self.main, self.right_element, None, ("100%",50))
		self.end_turn_button = Button(self.main, self.right_element, None, ("100%",self.main.font.get_height()))
		self.ready_button = Button(self.main, self.right_element, None, ("100%",self.main.font.get_height()))
		self.decks_element = Element(self.main, self.right_element, None, ("100%",75))
		self.public_goals_element = Element(self.main, self.right_element, None, ("100%","100%"))

		self.player_list_element.add_handler_keydown(self)
		self.decks_element.add_handler_keydown(self)
		self.public_goals_element.add_handler_keydown(self)

		self.end_turn_button.add_handler_submit(self)
		self.ready_button.add_handler_submit(self)

		self.end_turn_button.set_text("END TURN")
		self.ready_button.set_text("TOGGLE READY")

		self.end_turn_button.set_text_color((255,127,127))
		self.ready_button.set_text_color((127,255,127))

		self.end_turn_button.set_bg((255,127,127))
		self.ready_button.set_bg((127,255,127))
		self.decks_element.set_bg((175,125,175))
		self.public_goals_element.set_bg((173,204,227))

		self.player_list_element.layout = LAYOUT_VERTICAL
		self.public_goals_element.layout = LAYOUT_VERTICAL

		self.public_goals_element.v_scrollable = True
		self.public_goals_element.always_show_v_scroll = True

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
				element = Element(self.main,self.player_list_element,None,("100%",self.main.font.get_height()),bg_color,color)
				element.set_text(name)
		elif message.startswith("PLAYERHAND:"):
			hand = message[len("PLAYERHAND:"):].split(",")
			self.bottom_element.clear()
			self.bottom_element.layout = LAYOUT_HORIZONTAL
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
					element.menu_info = [("Play Card", self.do_nothing),
										 ("Action: Replace", self.do_nothing),
										 ("Discard", self.do_nothing)]
				elif card.type == "ship":
					element.menu_info = [("Play Card", self.do_nothing),
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
			self.table_element.clear()
			scale = 0.4
			grid_scale = 0.6
			size = (int(CARD_SIZE[0]*scale),int(CARD_SIZE[1]*scale))
			grid_size = (int(CARD_SIZE[0]*grid_scale), int(CARD_SIZE[1]*grid_scale))
			for y in xrange(self.main.card_table.size[1]):
				for x in xrange(self.main.card_table.size[0]):
					card = self.main.card_table.pony_cards[y][x]
					if card != None:
						pos = 	((grid_size[0] - size[0]) / 2,
									(grid_size[1] - size[1]) / 2)
						element = CardElement(self.main,self.table_element,pos,size)
						element.set_card(card)
						element.menu_info = [("Discard", self.do_nothing),
											 ("Action: Swap", self.do_nothing),
											 ("Action: Set Gender", self.do_nothing),
											 ("Action: Set Race", self.do_nothing),
											 ("Action: Give Keyword", self.do_nothing),
											 ("Action: Imitate Card", self.do_nothing)]
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
		if widget == self.end_turn_button:
			self.main.client.send("END_TURN")
		elif widget == self.ready_button:
			self.main.client.send("READY")
		elif (not (self.chat_input_element == None)) and widget == self.chat_input_element:
			message = self.chat_input_element.text.strip()
			if len(message) > 0:
				self.main.client.send("CHAT:"+self.chat_input_element.text)
			self.bottom_element.give_focus()

	def handle_event_losefocus(self, widget):
		if (not (self.chat_input_element == None)) and widget == self.chat_input_element:
			self.main.main_element._remove_child(self.chat_input_element)
			self.chat_input_element = None