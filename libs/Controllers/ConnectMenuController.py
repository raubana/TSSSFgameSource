from Controller import*

from ..GUI.GUI import *

import string, os, random, math

from libs.encode import encode, decode

class ConnectMenuController(Controller):
	def init(self):
		for card in self.main.my_master_deck.cards:
			card.reset()

		#Clear the gui
		self.main.updated_elements = []
		self.main.main_element.clear()
		self.main.main_element.set_text("")

		self.main.updated_elements.append(self)

		self.main.main_element.layout = LAYOUT_VERTICAL

		#loads and sets up the twilight head
		twilight_img = pygame.image.load("imgs/misc/twilight_peak.png")
		scale = 0.5
		self.twilight_img = pygame.transform.smoothscale( twilight_img,
														 (int(twilight_img.get_width()*scale),
														  int(twilight_img.get_height()*scale)))
		self.twilight_element = Element(self.main,
										self.main.main_element,
										(self.main.screen_size[0]-self.twilight_img.get_width()-25,
										 self.main.screen_size[1]),
										self.twilight_img.get_size(),
										bg=ScaleImage(self.twilight_img))
		self.twilight_peak_delay = 0.75
		self.twilight_peak_duration = 2.5
		self.twilight_peak_start_time = float(self.main.time)-self.twilight_peak_delay-self.twilight_peak_duration

		#loads the title
		title_img = pygame.image.load("imgs/misc/tsssf_title.png")
		scale = 0.75
		self.title_img = pygame.transform.smoothscale( title_img,
														 (int(title_img.get_width()*scale),
														  int(title_img.get_height()*scale)))
		self.title_element = Element(self.main,
										self.main.main_element,
										None,
										self.title_img.get_size(),
										bg=ScaleImage(self.title_img))
		self.title_element.margin = [10,10,0,10]

		#sets up the rest of the GUI
		text = "Version "+CLIENT_VERSION
		version_element = Element(self.main, self.main.main_element, None, self.main.font.size(text), None, text_color=(96,96,96))
		version_element.text = text
		version_element.margin = [10,0,0,2+self.main.font.get_height()]

		#element2 = Element(self.main, self.main.main_element, None, self.main.font.size("Please note that elements have been moved around."), None, text_color=(0,96,0))
		#element2.text = "Please note that elements have been moved around."
		#element2.margin = [10,10,0,10]

		element4 = Element(self.main, self.main.main_element, None, self.main.font.size("NAME"), None, text_color=(32,32,32))
		element4.text = "NAME"
		element4.margin = [10,0,0,2]

		self.name_inputbox = InputBox(self.main, self.main.main_element, None, (self.main.font.size("M"*PLAYERNAME_MAX_LENGTH)[0]+4, self.main.font.get_height()+4), (255,255,255))
		self.name_inputbox.margin = [10,0,0,2]
		self.name_inputbox.legal_characters = string.letters + string.digits + " "
		self.name_inputbox.max_characters = PLAYERNAME_MAX_LENGTH

		tooltip = "This is for users with reserved names.\nThese names are usually admins.\nYou don't need to type anything in here."

		element6 = Element(self.main, self.main.main_element, None, self.main.font.size("USER PASSWORD"), None, text_color=(32,32,32))
		element6.text = "USER PASSWORD"
		element6.margin = [10,0,0,2]
		element6.tooltip = tooltip

		self.password_inputbox = InputBox(self.main, self.main.main_element, None, (self.main.font.size("M"*20)[0]+4, self.main.font.get_height()+4), (255,255,255))
		self.password_inputbox.margin = [10,0,0,2]
		self.password_inputbox.legal_characters = string.letters + string.digits
		self.password_inputbox.max_characters = 20
		self.password_inputbox.hide_password = True
		self.password_inputbox.tooltip = tooltip

		tooltip = "This is for reserving a slot on a server, in case you disconnect.\nRight click for more options."

		element5 = Element(self.main, self.main.main_element, None, self.main.font.size("KEY"), None, text_color=(32,32,32))
		element5.text = "KEY"
		element5.margin = [10,0,0,2]
		element5.tooltip = tooltip

		self.key_inputbox = InputBox(self.main, self.main.main_element, None, (self.main.font.size("M"*5)[0]+4, self.main.font.get_height()+4), (255,255,255))
		self.key_inputbox.margin = [10,0,0,2]
		self.key_inputbox.legal_characters = string.letters + string.digits
		self.key_inputbox.max_characters = 5
		self.key_inputbox.tooltip = tooltip
		self.key_inputbox.menu_info.append(("generate new key",self.generate_new_key))

		#self.genkey_button = Button(self.main, self.main.main_element, None, (self.main.font.size("generate new key")[0]+5,self.main.font.get_height()+5), (255,255,255))
		#self.genkey_button.text = "generate new key"
		#self.genkey_button.margin = [10,0,0,25]
		
		element1 = Element(self.main, self.main.main_element, None, self.main.font.size("IP ADDRESS"), None, text_color=(32,32,32))
		element1.text = "IP ADDRESS"
		element1.margin = [10,0,0,2]

		self.ip_inputbox = InputBox(self.main, self.main.main_element, None, (self.main.font.size("MMM.MMM.MMM.MMM")[0]+4,self.main.font.get_height()+4), (255,255,255))
		self.ip_inputbox.margin = [10,0,0,2]
		if not DEBUG_LOCALHOST:
			self.ip_inputbox.legal_characters = "1234567890."
		self.ip_inputbox.max_characters = len("MMM.MMM.MMM.MMM")

		element2 = Element(self.main, self.main.main_element, None, self.main.font.size("PORT"), None, text_color=(32,32,32))
		element2.text = "PORT"
		element2.margin = [10,0,0,2]

		self.port_inputbox = InputBox(self.main, self.main.main_element, None, (self.main.font.size("M"*5)[0]+4,self.main.font.get_height()+4), (255,255,255))
		self.port_inputbox.margin = [10,0,0,2]
		self.port_inputbox.legal_characters = "1234567890"
		self.port_inputbox.max_characters = 5

		self.connect_button = Button(self.main, self.main.main_element, None, (self.main.font.size("CONNECT")[0]+15,self.main.font.get_height()+15), (255,255,255))
		self.connect_button.text = "CONNECT"
		self.connect_button.margin = [10,10,0,10]

		self.message_element = Element(self.main, self.main.main_element, None, ("100%",self.main.font.get_height()), None, text_color=(127,0,0))
		self.message_element.text = ""
		self.message_element.margin = [10,0,0,0]

		#Sets up handling
		self.ip_inputbox.add_handler_losefocus(self)
		self.port_inputbox.add_handler_losefocus(self)
		self.name_inputbox.add_handler_losefocus(self)

		self.ip_inputbox.add_handler_valuechange(self)
		self.port_inputbox.add_handler_valuechange(self)
		self.name_inputbox.add_handler_valuechange(self)

		self.ip_inputbox.add_handler_submit(self)
		self.port_inputbox.add_handler_submit(self)
		self.name_inputbox.add_handler_submit(self)
		self.key_inputbox.add_handler_submit(self)
		self.password_inputbox.add_handler_submit(self)
		#self.genkey_button.add_handler_submit(self)
		self.connect_button.add_handler_submit(self)

		self.load_from_appdata()

	def update(self):
		t_dif = self.main.time - self.twilight_peak_start_time
		if t_dif < self.twilight_peak_delay:
			p = 0
		elif t_dif > self.twilight_peak_delay + self.twilight_peak_duration:
			p = 1
		else:
			p = (t_dif-self.twilight_peak_delay) / float(self.twilight_peak_duration)
			p = math.sin(p*math.pi*0.5)
		size = self.twilight_img.get_size()
		pos = 	(max(int(self.main.screen_size[0] - size[0] - 25), 300),
				int(self.main.screen_size[1] - lerp(0,size[1],p)))

		self.twilight_element.set_pos(pos)

	def load_from_appdata(self):
		if APPDATA_LOCATION != None:
			folders = os.listdir(APPDATA_LOCATION)
			if "TSSSF" not in folders:
				os.makedirs(DATA_LOCATION)
			else:
				files = os.listdir(DATA_LOCATION)
				filename = "connectmenu.data"
				if filename in files:
					f = open(DATA_LOCATION+"/"+filename)
					try:
						data = f.read().split("\n")
						ip = data[0]
						port = data[1]
						name = data[2]
						key = data[3]
						password = data[4]
						self.ip_inputbox.set_text(ip)
						self.port_inputbox.set_text(port)
						self.name_inputbox.set_text(name)
						self.key_inputbox.set_text(key)
						self.password_inputbox.set_text(decode(password))
						f.close()
					except:
						f.close()
						os.remove(DATA_LOCATION+"/"+filename)
						print "ERROR! Failed to parse 'connectmenu.data'. File is deleted."

	def save_to_appdata(self):
		if DATA_LOCATION != None:
			filename = DATA_LOCATION+"/connectmenu.data"
			f = open(filename,"w")
			data = self.ip_inputbox.text+"\n"+self.port_inputbox.text+"\n"+self.name_inputbox.text+"\n"+self.key_inputbox.text+"\n"+encode(self.password_inputbox.text)
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
				self.save_to_appdata()
				self.main.connect_data = (str(self.ip_inputbox.text), int(self.port_inputbox.text), str(self.name_inputbox.text), str(self.key_inputbox.text), encode(str(self.password_inputbox.text)))
				import AttemptConnectController
				self.main.controller = AttemptConnectController.AttemptConnectController(self.main)
				print "IS ALL LEGAL"

	def generate_new_key(self):
		legal_characters = string.letters + string.digits
		key = ""
		for i in xrange(5):
			key += random.choice(legal_characters)
		self.key_inputbox.set_text(key)

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
		if DEBUG_LOCALHOST:
			if text != "localhost":
				message = "IP: DEBUG_LOCALHOST is True, port must be 'localhost'."
				legal = False
		else:
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
		if legal and not DEBUG_LOCALHOST:
			parts = text.split(".")
			for part in parts:
				num = int(part)
				if num < 0 or num > 255:
					message = "IP: Numbers in IP can't be smaller than 0 nor larger than 255."
					legal = False
					break
		if len(text) == 0 or legal:
			self.ip_inputbox.set_bg((255,255,255))
		else:
			self.ip_inputbox.set_bg((255,192,192))
		return message

	def check_port_is_legal(self):
		message = None
		text = str(self.port_inputbox.text)
		legal = True
		if DEBUG_LOCALHOST:
			if text != str(DEFAULT_PORT):
				message = "PORT: DEBUG_LOCALHOST is True, port must be '"+str(DEFAULT_PORT)+"'."
				legal = False
		else:
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
			self.port_inputbox.set_bg((255,255,255))
		else:
			self.port_inputbox.set_bg((255,192,192))
		return message

	def check_name_is_legal(self):
		message = None
		text = str(self.name_inputbox.text)
		legal = True
		if len(text) < 2:
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
			if (len(text) >= 4 and alpha_count < 3) or (len(text) < 4 and alpha_count < len(text) - 1):
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
			self.name_inputbox.set_bg((255,255,255))
		else:
			self.name_inputbox.set_bg((255,192,192))
		return message