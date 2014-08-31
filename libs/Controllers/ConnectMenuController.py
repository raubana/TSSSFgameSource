from Controller import*

from ..GUI.GUI import *

import string, os

class ConnectMenuController(Controller):
	def init(self):
		#Clear the gui
		self.main.updated_elements = []
		self.main.main_element.clear()
		self.main.main_element.set_text("")
		
		element1 = Element(self.main, self.main.main_element, None, ("100%",self.main.font.get_height()), None, text_color=(96,96,96))
		element1.text = "IP ADDRESS"
		element1.margin = [10,10,2,2]

		self.ip_inputbox = InputBox(self.main, self.main.main_element, None, (self.main.font.size("000000000000000")[0]+4,self.main.font.get_height()+4), (255,255,255))
		self.ip_inputbox.margin = [10,2,2,2]
		self.ip_inputbox.legal_characters = "1234567890."
		self.ip_inputbox.max_characters = len("000_000_000_000")

		element2 = Element(self.main, self.main.main_element, None, ("100%",self.main.font.get_height()), None, text_color=(96,96,96))
		element2.text = "PORT"
		element2.margin = [10,2,2,2]

		self.port_inputbox = InputBox(self.main, self.main.main_element, None, (self.main.font.size("00000")[0]+4,self.main.font.get_height()+4), (255,255,255))
		self.port_inputbox.margin = [10,2,2,2]
		self.port_inputbox.legal_characters = "1234567890"
		self.port_inputbox.max_characters = len("00000")

		element3 = Element(self.main, self.main.main_element, None, ("100%",0), None)
		element3.margin = [0,0,1,0]

		self.paste_button = Button(self.main, self.main.main_element, None, (self.main.font.size("PASTE ADDRESS")[0]+5,self.main.font.get_height()+5), (255,255,255))
		self.paste_button.text = "PASTE ADDRESS"
		self.paste_button.margin = [10,2,2,25]

		element4 = Element(self.main, self.main.main_element, None, ("100%",self.main.font.get_height()), None, text_color=(96,96,96))
		element4.text = "NAME"
		element4.margin = [10,2,2,2]

		self.name_inputbox = InputBox(self.main, self.main.main_element, None, (self.main.font.size("123456789012345")[0]+4, self.main.font.get_height()+4), (255,255,255))
		self.name_inputbox.margin = [10,2,2,2]
		self.name_inputbox.legal_characters = string.letters + string.digits + " "
		self.name_inputbox.max_characters = len("123456789012345")

		element5 = Element(self.main, self.main.main_element, None, ("100%",0), None)
		element5.margin = [0,0,1,22]

		self.connect_button = Button(self.main, self.main.main_element, None, (self.main.font.size("CONNECT")[0]+15,self.main.font.get_height()+15), (255,255,255))
		self.connect_button.text = "CONNECT"
		self.connect_button.margin = [10,2,2,2]

		self.message_element = Element(self.main, self.main.main_element, None, ("100%",self.main.font.get_height()), None, text_color=(127,0,0))
		self.message_element.text = ""
		self.message_element.margin = [10,2,2,2]

		#Sets up handling
		self.ip_inputbox.add_handler_losefocus(self)
		self.port_inputbox.add_handler_losefocus(self)
		self.name_inputbox.add_handler_losefocus(self)

		self.ip_inputbox.add_handler_valuechange(self)
		self.port_inputbox.add_handler_valuechange(self)
		self.name_inputbox.add_handler_valuechange(self)

		self.ip_inputbox.add_handler_submit(self)
		self.port_inputbox.add_handler_submit(self)
		self.paste_button.add_handler_submit(self)
		self.name_inputbox.add_handler_submit(self)
		self.connect_button.add_handler_submit(self)

		self.load_from_appdata()

	def load_from_appdata(self):
		folders = os.listdir(APPDATA_LOCATION)
		if "TSSSF" not in folders:
			os.makedirs(DATA_LOCATION)
		else:
			files = os.listdir(DATA_LOCATION)
			filename = "connectmenu.data"
			if filename in files:
				f = open(DATA_LOCATION+"/"+filename)
				data = f.read().split("\n")
				ip = data[0]
				port = data[1]
				name = data[2]
				self.ip_inputbox.set_text(ip)
				self.port_inputbox.set_text(port)
				self.name_inputbox.set_text(name)
				f.close()

	def save_to_appdata(self):
		filename = DATA_LOCATION+"/connectmenu.data"
		f = open(filename,"w")
		data = self.ip_inputbox.text+"\n"+self.port_inputbox.text+"\n"+self.name_inputbox.text
		f.write(data)
		f.close()

	def handle_event_losefocus(self, widget):
		self.check_widget(widget)

	def handle_event_valuechange(self, widget):
		self.check_widget(widget)

	def handle_event_submit(self, widget):
		if widget in (self.ip_inputbox,self.port_inputbox,self.name_inputbox,self.connect_button):
			m1 = self.check_ip_is_legal()
			legal = (m1 == None)
			m2 = self.check_port_is_legal()
			legal = (m2 == None) and legal
			m3 = self.check_name_is_legal()
			legal = (m3 == None) and legal
			message = None
			if m1 != None:
				message = m1
			elif m2 != None:
				message = m2
			elif m3 != None:
				message = m3
			if message:
				self.message_element.set_text(message)
			else:
				self.message_element.set_text("")

			if legal:
				#TODO: Attempt to make connection
				self.save_to_appdata()
				self.main.connect_data = (str(self.ip_inputbox.text), int(self.port_inputbox.text), str(self.name_inputbox.text))
				import AttemptConnectController
				self.main.controller = AttemptConnectController.AttemptConnectController(self.main)
				print "IS ALL LEGAL"
		elif widget == self.paste_button:
			#first we need to get the data off of the clipboard
			data = pygame.scrap.get(SCRAP_TEXT)
			message = "Address pasted from clipboard"
			if data:
				message = "Oh... uh, this doesn't work yet lol."
			else:
				message = "There doesn't appear to be any text on the clipboard."
			self.message_element.set_text(message)

	def check_widget(self, widget):
		message = None
		if widget == self.ip_inputbox:
			message = self.check_ip_is_legal()
		elif widget == self.port_inputbox:
			message = self.check_port_is_legal()
		elif widget == self.name_inputbox:
			message = self.check_name_is_legal()
		if message != None:
			self.message_element.set_text(message)
		else:
			self.message_element.set_text("")

	def check_ip_is_legal(self):
		message = None
		text = str(self.ip_inputbox.text)
		legal = True
		if len(text) < 7:
			legal = False
			message = "IP: IP is too short."
		elif text.count(".") < 3:
			legal = False
			message = "IP: IP is missing one or more periods."
		else:
			for i in xrange(len(text)):
				if text[i] == ".":
					if i - 1 >= 0 and i + 1 < len(text):
						if text[i-1] not in string.digits or text[i+1] not in string.digits:
							legal = False
							message = "IP: Can only have digits to left and right of a period."
							break
					else:
						message = "IP: IP can't start nor end with a period."
						legal = False
						break
		if legal:
			parts = text.split(".")
			for part in parts:
				num = int(part)
				if num < 0 or num > 255:
					message = "IP: Numbers in IP can't be smaller than 0 nor larger than 255."
					legal = False
					break
		if len(text) == 0 or legal:
			self.ip_inputbox.set_bg_color((255,255,255))
		else:
			self.ip_inputbox.set_bg_color((255,192,192))
		return message

	def check_port_is_legal(self):
		message = None
		text = str(self.port_inputbox.text)
		legal = True
		if len(text) < 3:
			message = "PORT: Port is too short."
			legal = False
		elif int(text) < 1024:
			message = "PORT: Port number is too small."
			legal = False
		elif int(text) > 65535:
			message = "PORT: Port number is too large."
			legal = False
		if len(text) == 0 or legal:
			self.port_inputbox.set_bg_color((255,255,255))
		else:
			self.port_inputbox.set_bg_color((255,192,192))
		return message

	def check_name_is_legal(self):
		message = None
		text = str(self.name_inputbox.text)
		legal = True
		if len(text) < 3:
			message = "NAME: Name is too short."
			legal = False
		elif text[0] == " " or text[-1] == " ":
			message = "NAME: Name can't begin nor end with a space."
			legal = False
		else:
			alpha_count = 0
			digit_count = 0
			space_count = 0
			for ch in text:
				if ch in string.letters:
					alpha_count += 1
				elif ch in string.digits:
					digit_count += 1
				elif ch in " ":
					space_count += 1
			if alpha_count < 3:
				message = "NAME: Name needs more alphabet characters."
				legal = False
			elif digit_count > 3:
				message = "NAME: Name has too many digits."
				legal = False
			elif space_count > 3:
				message = "NAME: Name has too many spaces."
				legal = False
		if legal:
			consec_spaces = 0
			for ch in text:
				if ch == " ":
					consec_spaces += 1
				else:
					consec_spaces = 0
				if consec_spaces >= 2:
					message = "NAME: Name has too many consecutive spaces."
					legal = False
					break
		if len(text) == 0 or legal:
			self.name_inputbox.set_bg_color((255,255,255))
		else:
			self.name_inputbox.set_bg_color((255,192,192))
		return message