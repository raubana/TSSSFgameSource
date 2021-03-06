import Deck

class Player(object):
	def __init__(self,address,name,player_key):
		self.address = address
		self.name = name
		self.player_key = player_key

		self.is_connected = True # This is for a player who may have disconnected and has a chance to reconnect
		self.is_loaded = False # This is for if a player has connected, but may or may not have downloaded the deck
		self.time_of_disconnect = 0 # This is the time when the player became disconnected, if they disconnected
		self.is_pinged = False # This is for if the player had to be pinged to check that they're still connected

		self.is_admin = False
		self.is_dev = False

		self.reset()

	def reset(self):
		self.hand = Deck.Deck()
		self.won_goals = Deck.Deck()
		self.is_ready = False # This is the players vote regarding starting the game or not
		self.last_toggled_ready = 0

		self.is_spectating = True

		self.reset_at_turns_end()

	def reset_at_turns_end(self):
		self.ponies_played = 0

	def get_score(self):
		score = 0
		for card in self.won_goals.cards:
			score += card.worth
		return score

