from Controller import*

from ..GUI.GUI import *

import string, os, random

class StartUpController(Controller):
	def init(self):
		#Clear the gui
		self.main.updated_elements = []
		self.main.main_element.clear()
		self.main.main_element.set_text("")

		self.main.set_text("Loading...")

		self.rendered_once = False

	def update(self):
		if self.rendered_once:
			self.main.my_master_deck.load_all_cards()
			import ConnectMenuController
			self.main.controller = ConnectMenuController.ConnectMenuController(self.main)

	def render(self):
		self.rendered_once = True
