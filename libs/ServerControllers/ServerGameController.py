from ServerController import ServerController

from ..ServerPlayer import Player
from ..locals import *

import time

class ServerGameController(ServerController):
	def init(self):
		self.gameserver.server.sendall("GAME_START")

	def read_message(self, message, player):
		return False