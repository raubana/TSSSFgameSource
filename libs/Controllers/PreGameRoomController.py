from Controller import*

from ..gui.GUI import *
from ..netcom import Client

import string, os, thread

class PreGameRoomController(Controller):
	def init(self):
		#Clear the gui
		self.main.updated_elements = []
		self.main.main_element.clear()
		self.main.main_element.set_text("In lobby.")