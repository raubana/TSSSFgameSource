
SNAPSHOT_NULL = -1
SNAPSHOT_UNKNOWN = 0
SNAPSHOT_TURN_START = 1
SNAPSHOT_PLAY_CARD = 2
SNAPSHOT_DREW_CARD = 3


class SnapShot(object):
	def __init__(self):
		#TODO: Create snapshot class.
		self.description = ""
		self.id = None
		self.type = SNAPSHOT_NULL

class HistoryMachine(object):
	def __init__(self):
		self.history = []

	def take_snapshot(self):
		#TODO: Create snapshot function.
		pass

	def get_transmit(self):
		#TODO: Create get_transmit function.
		pass