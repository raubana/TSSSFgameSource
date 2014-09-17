import Deck

class Player(object):
	def __init__(self,address,name,player_key):
		self.address = address
		self.name = name
		self.player_key = player_key

		self.hand = Deck.Deck()

		self.is_connected = True # This is for a player who may have disconnected and has a chance to reconnect
		self.is_loaded = False # This is for if a player has connected, but may or may not have downloaded the deck
		self.is_ready = False # This is the players vote regarding starting the game or not
		self.last_toggled_ready = 0

		self.time_of_disconnect = 0 # This is the time when the player became disconnected, if they disconnected

		self.is_pinged = False # This is for if the player had to be pinged to check that they're still connected
