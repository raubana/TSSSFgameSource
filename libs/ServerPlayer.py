import Deck

class Player(object):
	def __init__(self,address,name):
		self.address = address
		self.name = name
		self.hand = Deck.Deck()

		self.is_pinged = False

		self.is_ready = False
		self.last_toggled_is_ready = 0
