import pygame
import string
from common import*

pygame.font.init()

CARDBACK_NULL = -1
CARDBACK_START = 0
CARDBACK_PONY = 1
CARDBACK_SHIP = 2
CARDBACK_GOAL = 3


SPRITE_0 = 0
SPRITE_1 = 1
SPRITE_2 = 2
SPRITE_3 = 3
SPRITE_4 = 4
SPRITE_23 = 5
SPRITE_ALICORN = 6
SPRITE_CHANGELING_ALICORN = 7
SPRITE_CHANGELING_EARTH = 8
SPRITE_CHANGELING_PEGASUS = 9
SPRITE_CHANGELING_UNICORN = 10
SPRITE_DFP = 11
SPRITE_EARTH = 12
SPRITE_FEMALE = 13
SPRITE_GOAL = 14
SPRITE_MALE = 15
SPRITE_MALE_FEMALE = 16
SPRITE_PEGASUS = 17
SPRITE_SHIP = 18
SPRITE_UNICORN = 19

DEFAULT_TITLE_FONT_SIZE = 55
DEFAULT_POWER_FONT_SIZE = 40

TITLE_FONT = pygame.font.Font("data/fonts/Barth_Regular.ttf",DEFAULT_TITLE_FONT_SIZE)
KEYWORDS_FONT = pygame.font.Font("data/fonts/Ubahn_newpony.ttf",40)
POWER_FONT= pygame.font.Font("data/fonts/Ubahn_newpony.ttf",DEFAULT_POWER_FONT_SIZE)
QUOTE_FONT = pygame.font.Font("data/fonts/LinLibertine_RI.ttf",28)
COPYRIGHT_FONT = pygame.font.Font("data/fonts/Ubahn-Light.ttf",17)
COPYRIGHT_FONT.set_bold(True)



def autowrap_text(text, font, max_width):
	lines = []
	for L in text.split("\n"):
		current_line = ""
		line = ""
		parts = L.split(" ")
		i = 0
		while i < len(parts):
			word = parts[i]
			line += word
			if font.size(line)[0] > max_width:
				if current_line != "":
					lines.append(str(current_line))
				else:
					lines.append(str(word))
					i += 1
				current_line = ""
				line = ""
			else:
				current_line = str(line)
				line += " "
				i += 1
		line = line.strip()
		if line != "":
			lines.append(line)
	return lines


def create_template_from_attributes(attr, image):
	card_type = CARDBACK_NULL
	card_img = image
	title = ""
	keywords = []
	power_description = ""
	quote = ""
	card_copyright = ""
	card_sprites = []
	title_font_size = 55
	power_font_size = 40

	if "type" in attr:
		if attr["type"] == "pony":
			card_type = CARDBACK_PONY
			if "power" in attr:
				if attr["power"].find("startcard") != -1:
					card_type = CARDBACK_START
		elif attr["type"] == "ship":
			card_type = CARDBACK_SHIP
			card_sprites.append(SPRITE_SHIP)
		elif attr["type"] == "goal":
			card_type = CARDBACK_GOAL
			card_sprites.append(SPRITE_GOAL)

	if "name" in attr:
		title = attr["name"]
		title = string.replace(title, "\\n", "\n")

	DFP = False

	if "keywords" in attr:
		kw = string.split(attr["keywords"],",")
		for keyword in kw:
			keyword = keyword.strip()
			if keyword not in ["DFP"]:
				keywords.append(keyword)
			else:
				if keyword == "DFP":
					DFP = True

	if "power_description" in attr:
		power_description = attr["power_description"]
		power_description = string.replace(power_description, "\\n", "\n")

	if "quote" in attr:
		quote = attr["quote"]
		quote = string.replace(quote, "\\n", "\n")

	if "copyright" in attr:
		card_copyright = attr["copyright"]

	if "gender" in attr:
		if attr["gender"] == "both":
			card_sprites.append(SPRITE_MALE_FEMALE)
		elif attr["gender"] == "male":
			card_sprites.append(SPRITE_MALE)
		elif attr["gender"] == "female":
			card_sprites.append(SPRITE_FEMALE)

	is_changeling = False

	if "power" in attr:
		if attr["power"].find("changeling") != -1:
			is_changeling = True

	if "race" in attr:
		if is_changeling:
			if attr["race"] == "alicorn":
				card_sprites.append(SPRITE_CHANGELING_ALICORN)
			elif attr["race"] == "unicorn":
				card_sprites.append(SPRITE_CHANGELING_UNICORN)
			elif attr["race"] == "pegasus":
				card_sprites.append(SPRITE_CHANGELING_PEGASUS)
			elif attr["race"] == "earth":
				card_sprites.append(SPRITE_CHANGELING_EARTH)
		else:
			if attr["race"] == "alicorn":
				card_sprites.append(SPRITE_ALICORN)
			elif attr["race"] == "unicorn":
				card_sprites.append(SPRITE_UNICORN)
			elif attr["race"] == "pegasus":
				card_sprites.append(SPRITE_PEGASUS)
			elif attr["race"] == "earth":
				card_sprites.append(SPRITE_EARTH)

	if DFP:
		card_sprites.append(SPRITE_DFP)

	if "worth" in attr:
		if attr["worth"] == "0":
			card_sprites.append(SPRITE_0)
		elif attr["worth"] == "1":
			card_sprites.append(SPRITE_1)
		elif attr["worth"] == "2":
			card_sprites.append(SPRITE_2)
		elif attr["worth"] == "3":
			card_sprites.append(SPRITE_3)
		elif attr["worth"] == "4":
			card_sprites.append(SPRITE_4)

	if "name_font_size" in attr:
		try:
			title_font_size = int(attr["name_font_size"])
		except:
			pass

	if "power_font_size" in attr:
		try:
			power_font_size = int(attr["power_font_size"])
		except:
			pass

	template = Templatizer(	card_type,
							card_img,
							title,
							keywords,
							power_description,
							quote,
							card_copyright,
							card_sprites,
							title_font_size,
							power_font_size)
	return template


class Templatizer(object):
	def __init__(self, cardback, card_img, title, keywords, power, quote, copyright, sprites, title_font_size=55, power_font_size=40):
		self.cardback = cardback
		self.card_img = card_img
		self.title = title
		self.keywords = keywords
		self.power = power
		self.quote = quote
		self.copyright = copyright
		self.sprites = sprites
		self.title_font_size = title_font_size
		self.power_font_size = power_font_size

	def generate_image(self):
		# starts with the surface we'll be blitting to
		img = pygame.Surface((788, 1088), pygame.SRCALPHA)
		img.fill((0,0,0,0))

		TITLE_FONT = pygame.font.Font("data/fonts/Barth_Regular.ttf",self.title_font_size)
		KEYWORDS_FONT = pygame.font.Font("data/fonts/Ubahn_newpony.ttf",40)
		POWER_FONT= pygame.font.Font("data/fonts/Ubahn_newpony.ttf",self.power_font_size)
		QUOTE_FONT = pygame.font.Font("data/fonts/LinLibertine_RI.ttf",28)
		COPYRIGHT_FONT = pygame.font.Font("data/fonts/Ubahn-Light.ttf",17)
		COPYRIGHT_FONT.set_bold(True)

		#loads the card back
		if self.cardback == CARDBACK_START:
			cardback = pygame.image.load("imgs/template/card/Start.png")
			color = (58,50,53)
			second_color = (237,239,239)
		elif self.cardback == CARDBACK_PONY:
			cardback = pygame.image.load("imgs/template/card/Pony.png")
			color = (69,43,137)
			second_color = (234,220,236)
		elif self.cardback == CARDBACK_SHIP:
			cardback = pygame.image.load("imgs/template/card/Ship.png")
			color = (206,27,105)
			second_color = (234,220,236)
		elif self.cardback == CARDBACK_GOAL:
			cardback = pygame.image.load("imgs/template/card/Goal.png")
			color = (18,57,98)
			second_color = None#this doesn't have a second color because goals don't have keywords
		else:
			cardback = pygame.image.load("imgs/template/card/Unknown.png")
			color = (64,64,64)
			second_color = (220,220,220)

		img.blit(pygame.transform.smoothscale(self.card_img, (600, 442)), (123, 164))

		img.blit(cardback, (0, 0))

		#we render the card title
		if self.title_font_size != DEFAULT_TITLE_FONT_SIZE:
			font = pygame.font.Font("data/fonts/Ubahn_newpony.ttf",self.title_font_size)
		else:
			font = TITLE_FONT
		title_lines = autowrap_text(self.title, TITLE_FONT, 560)
		line_spacing = int(TITLE_FONT.get_height()*0.15)
		height = (TITLE_FONT.get_height())*len(title_lines) - (line_spacing)*(len(title_lines)-1)
		mid = 100
		y_pos = mid - (height/2)
		for line in title_lines:
			#print "'"+line+"'"
			srf = TITLE_FONT.render(line,True,color)
			img.blit(srf,(173+550-srf.get_width(), y_pos))
			y_pos += srf.get_height()-line_spacing

		#we render the card's keywords
		if len(self.keywords) > 0 and second_color != None:
			keywords = string.join(self.keywords,", ")
			srf = KEYWORDS_FONT.render(keywords, True, second_color)
			rect = srf.get_rect(topright = (722,607))
			img.blit(srf,rect)

		#render the card's power
		if self.power_font_size != DEFAULT_POWER_FONT_SIZE:
			font = pygame.font.Font("data/fonts/Ubahn_newpony.ttf",self.power_font_size)
		else:
			font = POWER_FONT
		y_pos = 650 + font.get_height()*0.65
		power_lines = autowrap_text(self.power, font, 679)
		line_spacing = int(font.get_height()*0.05)
		for line in power_lines:
			#print "'"+line+"'"
			srf = font.render(line, True, color)
			rect = srf.get_rect(midtop = (395,y_pos))
			img.blit(srf,rect)
			y_pos += rect.height-line_spacing

		#render the card's quote
		quote_lines = autowrap_text(self.quote, QUOTE_FONT, 682)
		quote_lines.reverse()
		line_spacing = int(QUOTE_FONT.get_height()*0.05)
		y_pos = 1040
		for line in quote_lines:
			#print "'"+line+"'"
			srf = QUOTE_FONT.render(line, True, lerp_colors(color,(0,0,0),0.3))
			rect = srf.get_rect(midbottom = (395,y_pos))
			img.blit(srf,rect)
			y_pos -= rect.height-line_spacing

		#we render the card's copyright
		srf = COPYRIGHT_FONT.render(self.copyright,True,(255,255,255))
		rect = srf.get_rect(topright = (750,1055))
		img.blit(srf,rect)

		#next we gather all of the sprites we'll be needing
		topleft_sprites = []
		bottomleft_sprite = None

		for sp in self.sprites:
			#print sp
			#this is a sprite that goes in the bottom left corner
			if sp == SPRITE_DFP:
				bottomleft_sprite = pygame.image.load("imgs/template/symbols/DystopianFuture.png")
			elif sp == SPRITE_0:
				bottomleft_sprite = pygame.image.load("imgs/template/symbols/0.png")
			elif sp == SPRITE_1:
				bottomleft_sprite = pygame.image.load("imgs/template/symbols/1.png")
			elif sp == SPRITE_2:
				bottomleft_sprite = pygame.image.load("imgs/template/symbols/2.png")
			elif sp == SPRITE_3:
				bottomleft_sprite = pygame.image.load("imgs/template/symbols/3.png")
			elif sp == SPRITE_4:
				bottomleft_sprite = pygame.image.load("imgs/template/symbols/4.png")
			elif sp == SPRITE_23:
				bottomleft_sprite = pygame.image.load("imgs/template/symbols/23.png")
			#this is a sprite that goes in the top left corner
			elif sp == SPRITE_CHANGELING_ALICORN:
				topleft_sprites.append(pygame.image.load("imgs/template/symbols/ChangelingAlicorn.png"))
			elif sp == SPRITE_CHANGELING_EARTH:
				topleft_sprites.append(pygame.image.load("imgs/template/symbols/ChangelingEarthPony.png"))
			elif sp == SPRITE_CHANGELING_PEGASUS:
				topleft_sprites.append(pygame.image.load("imgs/template/symbols/ChangelingPegasus.png"))
			elif sp == SPRITE_CHANGELING_UNICORN:
				topleft_sprites.append(pygame.image.load("imgs/template/symbols/ChangelingUnicorn.png"))
			elif sp == SPRITE_ALICORN:
				topleft_sprites.append(pygame.image.load("imgs/template/symbols/Alicorn.png"))
			elif sp == SPRITE_EARTH:
				topleft_sprites.append(pygame.image.load("imgs/template/symbols/EarthPony.png"))
			elif sp == SPRITE_PEGASUS:
				topleft_sprites.append(pygame.image.load("imgs/template/symbols/Pegasus.png"))
			elif sp == SPRITE_UNICORN:
				topleft_sprites.append(pygame.image.load("imgs/template/symbols/Unicorn.png"))
			elif sp == SPRITE_MALE:
				topleft_sprites.append(pygame.image.load("imgs/template/symbols/Male.png"))
			elif sp == SPRITE_FEMALE:
				topleft_sprites.append(pygame.image.load("imgs/template/symbols/Female.png"))
			elif sp == SPRITE_MALE_FEMALE:
				topleft_sprites.append(pygame.image.load("imgs/template/symbols/MaleFemale.png"))
			elif sp == SPRITE_SHIP:
				topleft_sprites.append(pygame.image.load("imgs/template/symbols/Ship.png"))
			elif sp == SPRITE_GOAL:
				topleft_sprites.append(pygame.image.load("imgs/template/symbols/Goal.png"))

		#first we render the bottom left sprite
		if bottomleft_sprite != None:
			rect = bottomleft_sprite.get_rect(topleft = (60,540))
			img.blit(bottomleft_sprite, rect)

		#then we render the top left sprites
		height = 0
		for sp in topleft_sprites:
			height += sp.get_height()
		mid = 135
		y_pos = max(mid - (height/2), 55)
		for sprite in topleft_sprites:
			img.blit(sprite,(110-(sprite.get_width()/2), y_pos))
			y_pos += sprite.get_height()

		return img