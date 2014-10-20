import pygame

from GUI import *
from ..HistoryMachine import *

IMG_SNAPSHOT_NULL = pygame.image.load("imgs/history_icons/template.png")
IMG_SNAPSHOT_UNKNOWN = pygame.image.load("imgs/history_icons/unknown.png")
IMG_SNAPSHOT_TURN_START = pygame.image.load("imgs/history_icons/started_turn.png")
IMG_SNAPSHOT_PLAY_CARD = pygame.image.load("imgs/history_icons/played_card.png")
IMG_SNAPSHOT_DREW_CARD = pygame.image.load("imgs/history_icons/drew_card.png")
IMG_SNAPSHOT_DISCARD_FROM_GRID = pygame.image.load("imgs/history_icons/card_discarded_from_grid.png")


def get_image_for_history_icon(event_type):
	if event_type == SNAPSHOT_UNKNOWN: return IMG_SNAPSHOT_UNKNOWN
	elif event_type == SNAPSHOT_TURN_START: return IMG_SNAPSHOT_TURN_START
	elif event_type == SNAPSHOT_PLAY_CARD: return IMG_SNAPSHOT_PLAY_CARD
	elif event_type == SNAPSHOT_DREW_CARD: return IMG_SNAPSHOT_DREW_CARD
	elif event_type == SNAPSHOT_DISCARD_FROM_GRID: return IMG_SNAPSHOT_DISCARD_FROM_GRID
	return IMG_SNAPSHOT_NULL


class HistoryElement(Element):
	def init(self):
		pass

	def parse_full_history(self, message):
		self.clear()
		self.layout = LAYOUT_HORIZONTAL

		print message

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
