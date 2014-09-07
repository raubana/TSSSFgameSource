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
		self.main.left_element = Element(self.main, self.main.main_element, None, (100,"100%"))
		self.main.top_element = None
		self.main.main_element.children.append(None)
		self.main.right_element = Element(self.main, self.main.main_element, None, (200,"100%"))
		self.main.bottom_element = None
		self.main.main_element.children.append(None)
		self.main.table_element = None#Element(self.main, self.main.main_element, None, ("100%","100%"))
		self.main.main_element.children.append(None)