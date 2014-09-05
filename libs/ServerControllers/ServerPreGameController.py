from ServerController import ServerController

from ..ServerPlayer import Player
from ..locals import *

import time

class ServerPreGameController(ServerController):
	def init(self):
		self.timer_started = False
		self.timer_start_time = 0
		self.timer_count = None

	def update(self):
		t = time.time()
		if self.timer_started:
			if t-self.timer_start_time >= 1:
				self.timer_count -= 1
				if self.timer_count <= 0:
					self.timer_started = False
					import ServerGameStartingController
					self.gameserver.controller = ServerGameStartingController.ServerGameStartingController(self.gameserver)
				else:
					self.gameserver.server.sendall("ADD_CHAT:SERVER:"+"..."+str(self.timer_count)+"...")
					self.gameserver.server.sendall("ALERT_TIMER")
					self.timer_start_time = float(t)

	def read_message(self, message, player):
		if message != None:
			if message == "READY":
				t = time.time()
				if t - player.last_toggled_is_ready >= 2.5:
					player.last_toggled_is_ready = t
					if not player.is_ready:
						player.is_ready = True
						self.gameserver.server.sendall("ALERT_READY")
						self.gameserver.server.sendto(player.address,"ADD_CHAT:SERVER:"+player.name+" is ready")
						self.check_ready()
						self.send_players_ready_all()
					else:
						player.is_ready = False
						self.gameserver.server.sendall("ALERT_NOT_READY")
						self.gameserver.server.sendto(player.address,"ADD_CHAT:SERVER:"+player.name+" is NOT ready")
						self.check_ready()
						self.send_players_ready_all()
				else:
					self.gameserver.server.sendto(player.address,"ADD_CHAT:SERVER:You're doing that too frequently. Please wait 3 seconds before toggling again.")
			else:
				return False
		return True

	def triggerNewPlayer(self, player):
		self.check_ready()
		self.send_players_ready_all()

	def triggerPlayerDisconnect(self, player):
		self.check_ready()
		self.send_players_ready_all()

	def get_players_ready(self):
		s = "PLAYERS_READY:"
		i = 0
		while i < len(self.gameserver.players):
			s += str(int(self.gameserver.players[i].is_ready))
			if i != len(self.gameserver.players)-1:
				s += ","
			i += 1
		return s

	def send_players_ready_to(self, player, message = None):
		if message == None:
			message = self.get_players_ready()
		print "sending",message,"to",player.name,player.address
		self.gameserver.server.sendto(player.address, message)

	def send_players_ready_all(self):
		message = self.get_players_ready()
		for player in self.gameserver.players:
			self.send_players_ready_to(player, str(message))

	def check_ready(self, force = None):
		if force in (True, False):
			if force:
				self.players_ready = len(self.gameserver.players)
			else:
				self.players_ready = 0
			for player in self.gameserver.players:
				player.is_ready = bool(force)
		else:
			self.players_ready = 0
			for player in self.gameserver.players:
				self.players_ready += int(player.is_ready)

		if self.players_ready == len(self.gameserver.players) and len(self.gameserver.players) >= MIN_PLAYERS:
			if not self.timer_started:
				self.gameserver.server.sendall("ADD_CHAT:SERVER:All players are ready, the game will start in...")
				self.timer_started = True
				self.timer_start_time = time.time()
				self.timer_count = 10
		else:
			if self.timer_started:
				self.gameserver.server.sendall("ADD_CHAT:SERVER:Cancelled.")
				self.timer_started = False
