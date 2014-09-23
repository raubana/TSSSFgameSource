from Controller import*

from ..GUI.GUI import *

import string, os

class GameController(Controller):
	def init(self):
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

		self.top_element.set_bg((197,96,204))
		self.right_element.set_bg(None)
		self.bottom_element.set_bg((197,96,204))
		self.table_element.set_bg((198-16,185-16,224-16))

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
		self.decks_element.set_bg((197,96,204))
		self.public_goals_element.set_bg((173,204,227))

		self.player_list_element.layout = LAYOUT_VERTICAL
		self.public_goals_element.layout = LAYOUT_VERTICAL

		self.public_goals_element.v_scrollable = True
		self.public_goals_element.always_show_v_scroll = True

		self.chat_input_element = None

		self.bottom_element.give_focus()

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