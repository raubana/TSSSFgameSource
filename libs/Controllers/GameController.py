from Controller import*

from ..GUI.GUI import *
from ..GUI.DeckElement import *
from ..GUI.CardElement import *
from ..GUI.TimerElement import *
from ..GUI.TableElement import *
from ..GUI.HistoryGUI import *

import string, os, time

class GameController(Controller):
	def init(self):
		#we try to get the user's attention.
		if self.main.trayicon != None:
			self.main.trayicon.ShowBalloon("Connected!","You're now loaded and on the server.", 15*1000)

		self.main.client.throttled = True

		self.render_card_frequency = 0.5
		self.last_rendered_card = 0
		self.all_cards_rendered = bool(CLIENT_PRERENDER_DECK)

		#Clear the gui
		#LEVEL 0
		self.main.updated_elements = []
		self.main.main_element.clear()
		self.main.main_element.set_text("")
		#sets up main GUI
		self.main.main_element.layout = LAYOUT_SPLIT

		#LEVEL 1
		self.left_element = None#Element(self.main, self.main.main_element, None, (0,"100%"))
		self.main.main_element.children.append(None)
		self.top_element = Element(self.main, self.main.main_element, None, ("100%",75))
		self.right_element = Element(self.main, self.main.main_element, None, (150,"100%"))
		self.bottom_element = Element(self.main, self.main.main_element, None, ("100%",100))
		self.table_element = TableElement(self.main, self.main.main_element, None, ("100%","100%"))

		self.top_element.add_handler_keydown(self)
		self.right_element.add_handler_keydown(self)
		self.bottom_element.add_handler_keydown(self)
		self.table_element.add_handler_keydown(self)

		self.right_element.set_bg(None)
		self.bottom_element.set_bg((175,125,175))
		self.table_element.set_bg((182,169,208))

		self.right_element.layout = LAYOUT_VERTICAL
		self.top_element.layout = LAYOUT_VERTICAL
		self.bottom_element.layout = LAYOUT_VERTICAL

		self.table_element.h_scrollable = True
		self.table_element.v_scrollable = True
		self.table_element.always_show_v_scroll = True
		self.table_element.always_show_h_scroll = True
		self.table_element.allow_rightclick_multi_axis_scrolling = True
		self.table_element.force_fullrange_scrolling = True

		#LEVEL 2
		self.history_element = HistoryElement(self.main, self.top_element, None, ("100%",50))
		self.chat_element = Element(self.main, self.top_element, None, ("100%","100%"))
		self.player_list_element = Element(self.main, self.right_element, None, ("100%",10))
		self.timer_element = TimerElement(self.main, self.right_element, None, ("100%", int(self.main.timer_font.get_height()*1.2)))
		self.decks_element = Element(self.main, self.right_element, None, ("100%",75))
		self.public_goals_element = Element(self.main, self.right_element, None, ("100%","100%"))
		self.card_selection_element = Element(self.main, self.bottom_element, None, ("100%","0%"))
		self.player_hand_element = Element(self.main, self.bottom_element, None, ("100%","100%"))

		self.history_element.add_handler_keydown(self)
		self.chat_element.add_handler_keydown(self)
		self.player_list_element.add_handler_keydown(self)
		self.decks_element.add_handler_keydown(self)
		self.public_goals_element.add_handler_keydown(self)
		self.card_selection_element.add_handler_keydown(self)
		self.player_hand_element.add_handler_keydown(self)

		self.timer_element.add_handler_mousepress(self)

		self.timer_element.set_text_color((255,255,255))

		self.timer_element.font = self.main.timer_font

		self.timer_element.set_text_align(ALIGN_MIDDLE)

		self.history_element.set_bg((175,125,175))
		self.timer_element.set_bg((175,125,175))
		self.decks_element.set_bg((175,125,175))
		self.public_goals_element.set_bg((173,204,227))
		self.card_selection_element.set_bg((175/2,125/2,175/2))
		self.player_hand_element.set_bg((175,125,175))

		self.history_element.layout = LAYOUT_HORIZONTAL
		self.chat_element.layout = LAYOUT_VERTICAL
		self.player_list_element.layout = LAYOUT_VERTICAL
		self.public_goals_element.layout = LAYOUT_VERTICAL
		self.card_selection_element.layout = LAYOUT_HORIZONTAL
		self.player_hand_element.layout = LAYOUT_HORIZONTAL

		self.history_element.h_scrollable = True
		self.history_element.always_show_h_scroll = True
		self.chat_element.v_scrollable = True
		self.chat_element.always_show_v_scroll = True
		self.public_goals_element.v_scrollable = True
		self.public_goals_element.always_show_v_scroll = True
		self.card_selection_element.h_scrollable = True
		self.card_selection_element.always_show_h_scroll = True
		self.player_hand_element.h_scrollable = True
		self.player_hand_element.always_show_h_scroll = True

		self.chat_element.snag_at_bottom = True

		self.timer_element.menu_info.append(("End Turn", self.end_turn))

		#LEVEL 3
		self.pony_deck_wrapper_element = Element(self.main, self.decks_element, None, ("33%","50%"), bg=None)
		self.ship_deck_wrapper_element = Element(self.main, self.decks_element, None, ("50%","50%"), bg=None)
		self.goal_deck_wrapper_element = Element(self.main, self.decks_element, None, ("100%","50%"), bg=None)
		self.pony_discard_wrapper_element = Element(self.main, self.decks_element, None, ("33%","100%"), bg=None)
		self.ship_discard_wrapper_element = Element(self.main, self.decks_element, None, ("50%","100%"), bg=None)

		#LEVEL 4
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

		self.pony_deck_element.menu_info.append(("Draw 1",self.draw_1,tuple(["pony"])))
		self.pony_deck_element.menu_info.append(("Shuffle",self.shuffle_pony_deck))

		self.ship_deck_element.menu_info.append(("Draw 1",self.draw_1,tuple(["ship"])))
		self.ship_deck_element.menu_info.append(("Shuffle",self.shuffle_ship_deck))

		self.goal_deck_element.menu_info.append(("Shuffle",self.shuffle_goal_deck))
		self.goal_deck_element.menu_info.append(("Draw Goal",self.draw_goal))

		self.pony_discard_element.menu_info.append(("Draw Top",self.draw_1_discard,tuple(["pony"])))
		self.pony_discard_element.menu_info.append(("Draw...",self.do_nothing))
		self.pony_discard_element.menu_info.append(("Shuffle",self.shuffle_pony_discard))
		self.pony_discard_element.menu_info.append(("Swap Decks",self.do_nothing))

		self.ship_discard_element.menu_info.append(("Draw Top",self.draw_1_discard,tuple(["ship"])))
		self.ship_discard_element.menu_info.append(("Draw...",self.do_nothing))
		self.ship_discard_element.menu_info.append(("Shuffle",self.shuffle_ship_discard))
		self.ship_discard_element.menu_info.append(("Swap Decks",self.do_nothing))

		self.chat_input_element = None

		self.bottom_element.give_focus()

	def do_nothing(self):
		pass
	def end_turn(self):
		self.main.client.send("END_TURN")
	def play_card(self, args):
		self.main.client.send("PLAY_CARD:"+str(args[0]))
	def draw_1(self, args):
		self.main.client.send("DRAW_1:"+args[0])
	def discard_card(self, args):
		self.main.client.send("DISCARD_CARD:"+str(args[0]))
	def replace_card(self, args):
		self.main.client.send("REPLACE_CARD:"+str(args[0]))
	def new_goal(self, args):
		self.main.client.send("NEW_GOAL:"+str(args[0]))
	def win_goal(self, args):
		self.main.client.send("WIN_GOAL:"+str(args[0]))
	def shuffle_pony_deck(self):
		self.main.client.send("SHUFFLE_PONY_DECK")
	def shuffle_ship_deck(self):
		self.main.client.send("SHUFFLE_SHIP_DECK")
	def shuffle_goal_deck(self):
		self.main.client.send("SHUFFLE_GOAL_DECK")
	def shuffle_pony_discard(self):
		self.main.client.send("SHUFFLE_PONY_DISCARD")
	def shuffle_ship_discard(self):
		self.main.client.send("SHUFFLE_SHIP_DISCARD")
	def discard_goal(self, args):
		self.main.client.send("DISCARD_GOAL:"+str(args[0]))
	def draw_goal(self):
		self.main.client.send("DRAW_GOAL")
	def draw_1_discard(self,args):
		self.main.client.send("DRAW_1_DISCARD:"+str(args[0]))

	def read_message(self, message):
		if self._rm_add_chat(message): pass
		elif self._rm_playerlist(message): pass
		elif self._rm_playerhand(message): pass
		elif self._rm_cardselection(message): pass
		elif self._rm_publicgoals(message): pass
		elif self._rm_cardtable(message): pass
		elif self._rm_decks(message): pass
		elif self._rm_timer(message): pass
		elif self._rm_your_turn(message): pass
		elif self._rm_turn_almost_over(message): pass
		elif self._rm_history_full(message): pass
		elif self._rm_modified_card(message): pass
		elif self._rm_unmodified_card(message): pass
		else:
			return False
		return True

	#Message Parsing Functions
	def _rm_add_chat(self, message):
		if message.startswith("ADD_CHAT:"):
			chat = message[len("ADD_CHAT:"):]
			if len(self.chat_element.children) >= 25:
				self.chat_element._remove_child(self.chat_element.children[0])
			element = Element(self.main, self.chat_element, None, ("100%",self.main.font.get_height()))
			color = (0,0,0,255)
			bg_color = (255,255,255,127)
			if chat.startswith("SERVER:"):
				chat = chat[len("SERVER:"):]
				if chat.startswith("PM:"):
					text = chat[len("PM:"):]
					color = (64,0,32,255)
					bg_color = (255,127,196,127)
				else:
					text = chat
					color = (64,0,64,255)
					bg_color = (255,127,255,127)
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
					text = name+" "+msg
					color = (64,64,64,255)
				elif msg.startswith(">"):
					msg = msg[len(">"):]
					text = "> "+name+": "+msg
					color = (0,96,0,255)
				else:
					text = chat
				self.main.play_sound("chat")
			else:
				text = chat
			element.set_text(text)
			element.set_text_color(color)
			element.set_bg(bg_color)
			return True
		return False
	def _rm_playerlist(self, message):
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
			return True
		return False
	def _rm_playerhand(self, message):
		if message.startswith("PLAYERHAND:"):
			s = message[len("PLAYERHAND:"):]
			self.player_hand_element.clear()
			self.player_hand_element.layout = LAYOUT_HORIZONTAL
			if len(s) > 0:
				hand = s.split(",")
				hand.reverse()
				scale = 0.325
				size = (int(CARD_SIZE[0]*scale),int(CARD_SIZE[1]*scale))
				for x in xrange(len(hand)):
					s = hand[len(hand)-x-1]
					i = int(s)
					card = self.main.master_deck.cards[i]
					element = CardElement(self.main,self.player_hand_element,None,size)
					element.set_card(card)
					element.padding = (3,3,3,3)
					if card.type == "pony":
						element.menu_info = [("Play Card", self.play_card, tuple([i])),
											 ("Action: Replace", self.replace_card, tuple([i])),
											 ("Discard", self.discard_card, tuple([self.main.master_deck.cards.index(card)]))]
					elif card.type == "ship":
						element.menu_info = [("Play Card", self.play_card, tuple([i])),
											 ("Discard", self.discard_card, tuple([self.main.master_deck.cards.index(card)]))]
			return True
		return False
	def _rm_cardselection(self, message):
		if message.startswith("CARDSELECTION:"):
			s = message[len("CARDSELECTION:"):]
			self.card_selection_element.clear()
			self.card_selection_element.layout = LAYOUT_HORIZONTAL
			if len(s) > 0:
				hand = s.split(",")
				hand.reverse()
				scale = 0.325
				size = (int(CARD_SIZE[0]*scale),int(CARD_SIZE[1]*scale))
				for x in xrange(len(hand)):
					s = hand[len(hand)-x-1]
					i = int(s)
					card = self.main.master_deck.cards[i]
					element = CardElement(self.main,self.card_selection_element,None,size)
					element.set_card(card)
					element.padding = (3,3,3,3)
				self.card_selection_element.set_size(("100%", "75%"))
			else:
				self.card_selection_element.set_size(("100%", "0%"))
			return True
		return False
	def _rm_publicgoals(self, message):
		if message.startswith("PUBLICGOALS:"):
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
				element.menu_info = [("Win Goal", self.win_goal, tuple([self.main.master_deck.cards.index(card)])),
										("Discard", self.discard_goal, tuple([self.main.master_deck.cards.index(card)])),
									 	("Action: New Goal", self.new_goal, tuple([i]))]
			return True
		return False
	def _rm_cardtable(self, message):
		if message.startswith("CARDTABLE:"):
			s = message[len("CARDTABLE:"):]
			self.main.card_table.parse_message(self.main.master_deck, s)
			self.table_element.setup_grid()
			return True
		return False
	def _rm_decks(self, message):
		if message.startswith("DECKS:"):
			print message
			s = message[len("DECKS:"):]
			parts = s.split(":")
			if len(parts) == 2:
				part1 = parts[0].split(",")
				part2 = parts[1].split(",")
				if len(part1) == 5:
					try:
						pony = str(int(part1[0]))
						ship = str(int(part1[1]))
						goal = str(int(part1[2]))
						pony_discard = str(int(part1[3]))
						ship_discard = str(int(part1[4]))
						self.pony_deck_count_element.set_text(pony)
						self.ship_deck_count_element.set_text(ship)
						self.goal_deck_count_element.set_text(goal)
						self.pony_discard_count_element.set_text(pony_discard)
						self.ship_discard_count_element.set_text(ship_discard)
					except:
						print "ERROR! Received bad decks info. D"
					if len(part2) == 2:
						try:
							if part2[0] == "N":
								self.pony_discard_element.tooltip = None
								self.pony_discard_element.set_bg((255,255,255,127))
							else:
								card = self.main.master_deck.cards[int(part2[0])]
								self.pony_discard_element.tooltip = card
								self.pony_discard_element.set_bg(ScaleImage(card.get_image()))
							if part2[1] == "N":
								self.ship_discard_element.tooltip = None
								self.ship_discard_element.set_bg((255,255,255,127))
							else:
								card = self.main.master_deck.cards[int(part2[1])]
								self.ship_discard_element.tooltip = card
								self.ship_discard_element.set_bg(ScaleImage(card.get_image()))
						except:
							print "ERROR! Received bad decks info. E"
					else:
						print "ERROR! Received bad decks info. C"
				else:
					print "ERROR! Received bad decks info. B"
			else:
				print "ERROR! Received bad decks info. A"
			return True
		return False
	def _rm_timer(self, message):
		if message.startswith("TIMER:"):
			s = message[len("TIMER:"):]
			self.timer_element.set_text(s)
			return True
		return False
	def _rm_your_turn(self, message):
		if message == "YOUR_TURN":
			if not pygame.key.get_focused():
				self.main.play_sound("players_turn_not_focused", True)
				#we try to get the user's attention.
				if self.main.trayicon != None:
					self.main.trayicon.ShowBalloon("Yay!","It's your turn!", 15*1000)
			else:
				self.main.play_sound("players_turn")
			return True
		return False
	def _rm_turn_almost_over(self, message):
		if message == "TURN_ALMOST_OVER":
			if not pygame.key.get_focused():
				self.main.play_sound("players_turn_not_focused", True)
				#we try to get the user's attention.
				if self.main.trayicon != None:
					self.main.trayicon.ShowBalloon("Uh oh!","You're almost out of time!", 15*1000)
			else:
				self.main.play_sound("players_turn")
			return True
		return False
	def _rm_history_full(self, message):
		if message.startswith("HISTORY_FULL:"):
			s = message[len("HISTORY_FULL:"):]
			self.history_element.parse_full_history(s)
			return True
		return False
	def _rm_modified_card(self, message):
		if message.startswith("MODIFIED_CARD:"):
			s = message[len("MODIFIED_CARD:"):]
			parts = s.split("::")
			print parts
			if len(parts) == 9:
				id = int(parts[0])
				card = self.main.master_deck.cards[id]
				#Temp Gender::Temp Race::Temp Keywords::Temp To Be Discarded::Temp Card Being Imitated
				if parts[8] != "":
					card.imitate_card(self.main.master_deck.cards[int(parts[8])], self.main.master_deck)

				if parts[1] != "":
					name = parts[1]
				else:
					name = None
				if parts[2] != "":
					printed_name = parts[2]
				else:
					printed_name = None
				if parts[3] != "":
					printed_name_size = int(parts[3])
				else:
					printed_name_size = None
				card.set_temp_name(name, printed_name, printed_name_size)

				if parts[4] != "":
					gender = parts[4]
				else:
					gender = None
				card.set_temp_gender(gender)

				if parts[5] != "":
					race = parts[5]
				else:
					race = None
				card.set_temp_race(race)

				if parts[6] != "NONE":
					keywords = parts[6].split(",")
				else:
					keywords = None
				card.set_temp_keywords(keywords)

				if parts[7] == "True":
					to_be_discarded = True
				else:
					to_be_discarded = False
				card.set_temp_to_be_discarded(to_be_discarded)

				card.rerender()
				element = self.find_element_for_card(card)
				if element != None:
					element.set_card(card,element.alpha,element.angle)
			else:
				print "ERROR! Received bad modified card info. A"
			return True
		return False
	def _rm_unmodified_card(self, message):
		if message.startswith("UNMODIFIED_CARD:"):
			s = message[len("UNMODIFIED_CARD:"):]
			i = int(s)
			card = self.main.master_deck.cards[i]
			card.reset()

			card.rerender()
			element = self.find_element_for_card(card)
			if element != None:
				element.set_card(card,element.alpha,element.angle)
			return True
		return False

	#Misc. Functions
	def update(self):
		if not self.all_cards_rendered:
			t = time.time()
			if t-self.last_rendered_card >= self.render_card_frequency:
				self.last_rendered_card = t
				match = None
				for card in self.main.master_deck.cards:
					if card.flagged_for_rerender:
						match = card
						break
				if match:
					match.rerender()
				else:
					self.all_cards_rendered = True

	def find_element_for_card(self, card):
		for child in self.bottom_element.children:
			if type(child) == CardElement and child.card == card:
				return child
		for child in self.table_element.children:
			if type(child) == CardElement and child.card == card:
				return child
		for child in self.public_goals_element.children:
			if type(child) == CardElement and child.card == card:
				return child

	#Handler Functions
	def handle_event_keydown(self, widget, unicode, key):
		if key == K_RETURN:
			self.chat_input_element = InputBox(self.main, self.main.main_element, (25,25), ("100%-50px",self.main.font.get_height()+2))
			self.chat_input_element.max_characters = 100
			self.chat_input_element.add_handler_submit(self)
			self.chat_input_element.add_handler_losefocus(self)
			self.chat_input_element.give_focus()
			self.top_element.set_size(("100%","100%"))
		elif key == K_ESCAPE:
			self.main.client.send("CANCEL_ACTION")


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
			self.top_element.set_size(("100%",75))