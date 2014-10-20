import pygame

from GUI import *
from ..HistoryMachine import *

IMG_SNAPSHOT_NULL = pygame.image.load("imgs/history_icons/template.png")
IMG_SNAPSHOT_UNKNOWN = pygame.image.load("imgs/history_icons/unknown.png")
IMG_SNAPSHOT_TURN_START = pygame.image.load("imgs/history_icons/started_turn.png")
IMG_SNAPSHOT_PLAY_CARD = pygame.image.load("imgs/history_icons/played_card.png")
IMG_SNAPSHOT_DREW_CARD = pygame.image.load("imgs/history_icons/drew_card.png")


def get_image_for_history_icon(event_type):
	if event_type == SNAPSHOT_UNKNOWN: return IMG_SNAPSHOT_UNKNOWN
	elif event_type == SNAPSHOT_TURN_START: return IMG_SNAPSHOT_TURN_START
	elif event_type == SNAPSHOT_PLAY_CARD: return IMG_SNAPSHOT_PLAY_CARD
	elif event_type == SNAPSHOT_DREW_CARD: return IMG_SNAPSHOT_DREW_CARD
	return IMG_SNAPSHOT_NULL


class HistoryElement(Element):
	def init(self):
		pass

	def parse_full_history(self, message):
		pass
