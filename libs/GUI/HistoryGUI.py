import pygame

from GUI import *
from ..HistoryMachine import *

IMG_SNAPSHOT_NULL = pygame.image.load("imgs/history_icons/template.png")
IMG_SNAPSHOT_UNKNOWN = pygame.image.load("imgs/history_icons/unknown.png")
IMG_SNAPSHOT_TURN_START = pygame.image.load("imgs/history_icons/started_turn.png")
IMG_SNAPSHOT_PLAY_PONY_CARD = pygame.image.load("imgs/history_icons/played_pony_card.png")
IMG_SNAPSHOT_PLAY_SHIP_CARD = pygame.image.load("imgs/history_icons/played_ship_card.png")
IMG_SNAPSHOT_DREW_PONY_CARD = pygame.image.load("imgs/history_icons/drew_pony_card.png")
IMG_SNAPSHOT_DREW_SHIP_CARD = pygame.image.load("imgs/history_icons/drew_ship_card.png")
IMG_SNAPSHOT_DISCARD_FROM_GRID = pygame.image.load("imgs/history_icons/card_discarded_from_grid.png")
IMG_SNAPSHOT_NEW_GOAL = pygame.image.load("imgs/history_icons/new_goal.png")
IMG_SNAPSHOT_SWAP_GENDER = pygame.image.load("imgs/history_icons/swapped_gender.png")
IMG_SNAPSHOT_WIN_GOAL = pygame.image.load("imgs/history_icons/won_goal.png")


def get_image_for_history_icon(event_type):
	if event_type == SNAPSHOT_UNKNOWN: return IMG_SNAPSHOT_UNKNOWN
	elif event_type == SNAPSHOT_TURN_START: return IMG_SNAPSHOT_TURN_START
	elif event_type == SNAPSHOT_PLAY_PONY_CARD: return IMG_SNAPSHOT_PLAY_PONY_CARD
	elif event_type == SNAPSHOT_PLAY_SHIP_CARD: return IMG_SNAPSHOT_PLAY_SHIP_CARD
	elif event_type == SNAPSHOT_DREW_PONY_CARD: return IMG_SNAPSHOT_DREW_PONY_CARD
	elif event_type == SNAPSHOT_DREW_SHIP_CARD: return IMG_SNAPSHOT_DREW_SHIP_CARD
	elif event_type == SNAPSHOT_DISCARD_FROM_GRID: return IMG_SNAPSHOT_DISCARD_FROM_GRID
	elif event_type == SNAPSHOT_NEW_GOAL: return IMG_SNAPSHOT_NEW_GOAL
	elif event_type == SNAPSHOT_SWAP_GENDER: return IMG_SNAPSHOT_SWAP_GENDER
	elif event_type == SNAPSHOT_WIN_GOAL: return IMG_SNAPSHOT_WIN_GOAL
	return IMG_SNAPSHOT_NULL


class HistoryElement(Element):
	def init(self):
		pass

	def parse_full_history(self, message):
		self.clear()
		self.layout = LAYOUT_HORIZONTAL

		i = message.find(":")
		if i != -1:
			try:
				number_of_events = int(message[:i])
				works = True
			except:
				works = False
			if works:
				s = message[(i+1):]
				parts = s.split("::")
				if len(parts) == number_of_events:
					for part in parts:
						i = part.find(",")
						if i != -1:
							try:
								event_type = int(part[:i])
								works = True
							except:
								works = False
							if works:
								s = part[(i+1):]
								element = Element(self.main,self,None,(30,30),bg=ScaleImage(get_image_for_history_icon(event_type)))
								element.tooltip = s
							else:
								print "ERROR! Received bad full history! E"
						else:
							print "ERROR! Received bad full history! D"
				else:
					print "ERROR! Received bad full history! C"
			else:
				print "ERROR! Received bad full history! B"
		else:
			print "ERROR! Received bad full history! A"
