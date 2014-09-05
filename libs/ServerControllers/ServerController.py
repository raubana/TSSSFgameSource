__author__ = 'dylan_000'

class ServerController(object):
	def __init__(self, gameserver):
		self.gameserver = gameserver
		self.init()

	def init(self):
		pass

	def update(self):
		pass

	def read_message(self, message, player):
		pass

	def triggerNewPlayer(self, player):
		pass

	def triggerRejoinPlayer(self, player):
		pass#TODO: Default this to a full-update

	def triggerPlayerDisconnect(self, player):
		pass