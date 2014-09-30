import traceback

DEFAULT_COPYRIGHT = "Core 1.0.4 Copyright 2014 Horrible People Games. Art by Pixel Prism."

try:
	import Tkinter
	from PIL import Image, ImageTk
	from tkFileDialog import askopenfilename, asksaveasfilename

	import pickle
	import pygame.image, pygame.transform
	import gzip
	import tempfile
	import os
	import io
	import string

	import libs.PickledCard
	from libs.locals import *
	import libs.Deck
	import libs.Templatizer
except Exception, e:
	print traceback.format_exc()
	input("Press enter to quit.")

class Main(object):
	def __init__(self):
		self.filename = ""
		self.imported_image = None

		self.top = Tkinter.Tk()
		self.setup_main_gui()

		self.top.mainloop()

	def donothing(self):
		pass

	def quit(self):
		self.check_save_first()
		self.top.quit()

	def setup_main_gui(self):
		menu = Tkinter.Menu()
		menubar = Tkinter.Menu(self.top)
		filemenu = Tkinter.Menu(menubar, tearoff=0)
		filemenu.add_command(label="Generate (F5)", command=self.update_image)
		filemenu.add_command(label="Export Image", command=self.prompt_export_image)
		filemenu.add_separator()
		filemenu.add_command(label="New", command=self.close_file)
		filemenu.add_command(label="Import image", command=self.prompt_import_image)
		filemenu.add_command(label="Open", command=self.prompt_open_file)
		filemenu.add_command(label="Save", command=self.do_save_file)
		filemenu.add_command(label="Save as...", command=self.prompt_save_file)

		filemenu.add_separator()

		filemenu.add_command(label="Exit", command=self.quit)
		menubar.add_cascade(label="File", menu=filemenu)

		templatemenu = Tkinter.Menu(menubar, tearoff=0)
		templatemenu.add_command(label="Pony", command=self.set_template_pony)
		templatemenu.add_command(label="Ship", command=self.set_template_ship)
		templatemenu.add_command(label="Goal", command=self.set_template_goal)
		menubar.add_cascade(label="Template", menu=templatemenu)

		helpmenu = Tkinter.Menu(menubar, tearoff=0)

		helpmenu.add_command(label="Open Wiki", command=self.open_wiki)
		menubar.add_cascade(label="Help", menu=helpmenu)

		self.top.config(menu=menubar)

		self.main = Tkinter.Frame(self.top)
		self.main.pack(expand=True, fill=Tkinter.BOTH)
		self.main.bind("<F5>", self.handle_update_image)

		left_frame = Tkinter.Frame(self.main)
		left_frame.pack(side=Tkinter.LEFT, expand=True, fill=Tkinter.BOTH)

		right_frame = Tkinter.Frame(self.main)
		right_frame.pack(side=Tkinter.RIGHT, fill=Tkinter.Y)

		self.attributes = Tkinter.Text(right_frame)
		self.attributes.pack(fill=Tkinter.Y)
		self.attributes.bind("<F5>", self.handle_update_image)

		self.canvas = Tkinter.Canvas(left_frame, width=CARD_SIZE[0], height=CARD_SIZE[1])
		self.canvas.pack()

	def export_image(self, filename):
		if self.imported_image != None and filename != "":
			if not filename.endswith(".png"):
				filename += ".png"
			data = str(self.attributes.get("1.0", "1000000000.0"))
			data = data.strip()
			L = data.split("\n")
			attr = {}
			for l in L:
				try:
					spl = libs.Deck.break_apart_line(l)
					attr[spl[0]] = spl[1]
				except:
					pass
			if "template" in attr and attr["template"] == "True":
				template = libs.Templatizer.create_template_from_attributes(attr, self.imported_image)
				pygame.image.save(template.generate_image(),filename)

	def handle_update_image(self, event):
		self.update_image()

	def set_template_pony(self):
		self.attributes.delete(1.0, Tkinter.END)
		self.attributes.insert(Tkinter.INSERT, "type = pony\n")
		self.attributes.insert(Tkinter.INSERT, "name = \n")
		self.attributes.insert(Tkinter.INSERT, "keywords = \n")
		self.attributes.insert(Tkinter.INSERT, "gender = \n")
		self.attributes.insert(Tkinter.INSERT, "race = \n")
		self.attributes.insert(Tkinter.INSERT, "number_of_ponies = 1\n")
		self.attributes.insert(Tkinter.INSERT, "power = \n")
		self.attributes.insert(Tkinter.INSERT, "power_activates_on = default\n")
		self.attributes.insert(Tkinter.INSERT, "power_is_mandatory = False\n")
		self.attributes.insert(Tkinter.INSERT, "power_is_copyable = \n")
		self.attributes.insert(Tkinter.INSERT, "\n")
		self.attributes.insert(Tkinter.INSERT, "#Delete everything after this line, if you're not using card templates.\n")
		self.attributes.insert(Tkinter.INSERT, "template = False\n")
		self.attributes.insert(Tkinter.INSERT, "power_description = \n")
		self.attributes.insert(Tkinter.INSERT, "quote = \n")
		self.attributes.insert(Tkinter.INSERT, "copyright = "+DEFAULT_COPYRIGHT)

	def set_template_ship(self):
		self.attributes.delete(1.0, Tkinter.END)
		self.attributes.insert(Tkinter.INSERT, "type = ship\n")
		self.attributes.insert(Tkinter.INSERT, "name = \n")
		self.attributes.insert(Tkinter.INSERT, "power = \n")
		self.attributes.insert(Tkinter.INSERT, "power_activates_on = default\n")
		self.attributes.insert(Tkinter.INSERT, "power_is_mandatory = False\n")
		self.attributes.insert(Tkinter.INSERT, "\n")
		self.attributes.insert(Tkinter.INSERT, "#Delete everything after this line, if you're not using card templates.\n")
		self.attributes.insert(Tkinter.INSERT, "template = False\n")
		self.attributes.insert(Tkinter.INSERT, "power_description = \n")
		self.attributes.insert(Tkinter.INSERT, "quote = \n")
		self.attributes.insert(Tkinter.INSERT, "copyright = "+DEFAULT_COPYRIGHT)

	def set_template_goal(self):
		self.attributes.delete(1.0, Tkinter.END)
		self.attributes.insert(Tkinter.INSERT, "type = goal\n")
		self.attributes.insert(Tkinter.INSERT, "name = \n")
		self.attributes.insert(Tkinter.INSERT, "condition = \n")
		self.attributes.insert(Tkinter.INSERT, "worth = \n")
		self.attributes.insert(Tkinter.INSERT, "modifiers = None\n")
		self.attributes.insert(Tkinter.INSERT, "\n")
		self.attributes.insert(Tkinter.INSERT, "#Delete everything after this line, if you're not using card templates.\n")
		self.attributes.insert(Tkinter.INSERT, "template = False\n")
		self.attributes.insert(Tkinter.INSERT, "power_description = Win this Goal when:\\n\n")
		self.attributes.insert(Tkinter.INSERT, "quote = \n")
		self.attributes.insert(Tkinter.INSERT, "copyright = "+DEFAULT_COPYRIGHT)

	def getSuggestedFilename(self):
		# we need to get the text from the attributes widget
		data = str(self.attributes.get("1.0", "1000000000.0"))
		data = data.strip()
		L = data.split("\n")
		attr = {}
		for l in L:
			try:
				spl = libs.Deck.break_apart_line(l)
				attr[spl[0]] = spl[1]
			except:
				pass
		filename = ""
		if "type" in attr:
			t = str(attr["type"])
			if t == "pony":
				filename += "Pony"
			elif t == "ship":
				filename += "Ship"
			elif t == "goal":
				filename += "Goal"
			else:
				pass
		legal = list(string.ascii_letters + string.digits + " ")
		if "name" in attr:
			name = str(attr["name"]).strip()
			name = list(name)
			i = len(name) - 1
			while i >= 0:
				if name[i] not in legal:
					name.pop(i)
				i -= 1
			name = string.join(name, "")
			name = name.split(" ")
			i = len(name) - 1
			while i >= 0:
				if name[i] != "":
					part = list(string.lower(name[i]))
					part[0] = string.upper(part[0])
					part = string.join(part, "")
					name[i] = part
				i -= 1
			name = string.join(name, "")
			filename += name
		return filename

	def prompt_open_file(self):
		self.check_save_first()

		filename = askopenfilename(filetypes=[('Card file', '.tsf'), ('Card file', '.tsssf')], initialdir="cards")
		self.filename = filename
		self.load_file(filename)

	def prompt_import_image(self):
		filename = askopenfilename(filetypes=[('Png files', '.png')], initialdir="imgs/split pages")
		self.import_image(filename)

	def prompt_save_file(self):
		if self.imported_image != None:
			suggested_filename = self.getSuggestedFilename()
			self.filename = asksaveasfilename(filetypes=[('Card files', '.tsf'),('Old Card files', '.tsssf')], initialfile=suggested_filename,
											  initialdir="cards")
			self.save_file()

	def prompt_export_image(self):
		if self.imported_image != None:
			suggested_filename = self.getSuggestedFilename()
			filename = asksaveasfilename(filetypes=[('Png files', '.png')], initialfile=suggested_filename,
											  initialdir="cards")
			self.export_image(filename)

	def import_image(self, filename):
		if filename != "":
			self.imported_image = pygame.image.load(filename)
			self.update_image()

	def update_image(self):
		if self.imported_image != None:
			#first we parse our data to determine if our image is pregenerated or not.
			data = str(self.attributes.get("1.0", "1000000000.0"))
			data = data.strip()
			L = data.split("\n")
			attr = {}
			for l in L:
				try:
					spl = libs.Deck.break_apart_line(l)
					attr[spl[0]] = spl[1]
				except:
					pass

			if "template" in attr and attr["template"] == "True":
				#we have to generate the image.
				template = libs.Templatizer.create_template_from_attributes(attr, self.imported_image)
				self.card_image = pygame.transform.smoothscale(template.generate_image(),CARD_SIZE)
			else:
				#the image is pregenerated. Simply resize.
				self.card_image = pygame.transform.smoothscale(self.imported_image,CARD_SIZE)
			pygame.image.save(self.card_image,self.filename+".temp.png")
			img = Image.open(self.filename+".temp.png")
			img = img.resize(CARD_SIZE, Image.ANTIALIAS)
			img = ImageTk.PhotoImage(img)
			self.canvas.img = img
			self.canvas.create_image(CARD_SIZE[0] / 2, CARD_SIZE[1] / 2, image=img)
			os.remove(self.filename+".temp.png")

	def check_save_first(self):
		pass

	def do_save_file(self):
		if self.filename == "":
			self.prompt_save_file()
		else:
			self.save_file()

	def save_file(self):
		if self.filename != "" and self.imported_image != None:
			if not self.filename.endswith(".tsf") and not self.filename.endswith(".tsssf"):
				self.filename += ".tsf"
			# We need to make our object first.
			data = str(self.attributes.get("1.0", "1000000000.0"))
			data = data.strip()
			L = data.split("\n")
			attr = {}
			for l in L:
				try:
					spl = libs.Deck.break_apart_line(l)
					attr[spl[0]] = spl[1]
				except:
					pass
			if "template" in attr and attr["template"] == "True":
				imported_image = self.imported_image
				if imported_image.get_size() != CARD_ART_SIZE:
					imported_image = pygame.transform.smoothscale(imported_image, CARD_ART_SIZE)
				pygame.image.save(imported_image, self.filename+".temp.png")
			else:
				imported_image = self.imported_image
				if imported_image.get_size() != CARD_SIZE:
					imported_image = pygame.transform.smoothscale(imported_image, CARD_SIZE)
				pygame.image.save(imported_image, self.filename+".temp.png")
			f = io.FileIO(self.filename+".temp.png", "r")
			image_data = f.read()
			f.close()
			os.remove(self.filename+".temp.png")
			card = libs.PickledCard.PickledCard(image_data, data)
			libs.PickledCard.save_pickledcard(card, self.filename)

	def load_file(self, filename):
		if filename != "":
			self.main.destroy()
			self.setup_main_gui()
			card = libs.PickledCard.open_pickledcard(filename)
			self.attributes.insert(Tkinter.INSERT, card.attr)
			imgIO = io.BytesIO(card.img)
			self.filename = filename
			self.imported_image = pygame.image.load(imgIO)
			self.update_image()

	def close_file(self):
		self.check_save_first()

		self.filename = ""
		self.imported_image = None

		self.main.destroy()
		self.setup_main_gui()

	def open_wiki(self):
		import webbrowser
		webbrowser.open("http://tsssfgame.wikia.com/wiki/.tsssf")

try:
	main = Main()
except Exception, e:
	print traceback.format_exc()
	input("Press enter to quit.")