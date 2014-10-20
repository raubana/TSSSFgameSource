
SNAPSHOT_NULL = -1
SNAPSHOT_UNKNOWN = 0
SNAPSHOT_TURN_START = 1
SNAPSHOT_PLAY_CARD = 2
SNAPSHOT_DREW_CARD = 3


class Snapshot(object):
	def __init__(self, id, event_type = SNAPSHOT_NULL):
		#TODO: Create snapshot class.
		self.description = ""
		self.id = id
		self.event_type = event_type

	def get_transmit(self):
		s = ""
		s += str(self.event_type) + ","
		s += self.description
		return s


class HistoryMachine(object):
	def __init__(self):
		self.history = []

	def clear(self):
		self.history = []

	def take_snapshot(self, event_type, description):
		#TODO: Finish snapshot function.
		if len(self.history) == 0 or (self.history[-1].event_type != SNAPSHOT_NULL and self.history[-1].event_type != event_type):
			#Creates a new snapshot.
			self.history.append(Snapshot(len(self.history), event_type))
		snapshot = self.history[-1]
		if snapshot.description == "": snapshot.description = description
		else: snapshot.description += "\n" + description

	def get_full_transmit(self):
		#TODO: Finish get_full_transmit function.
		s = ""
		s += "HISTORY_FULL:"
		s += str(len(self.history))+":"
		i = 0
		while i < len(self.history):
			snapshot = self.history[i]
			s += snapshot.get_transmit()
			i += 1
			if i < len(self.history):
				s += "::"
		return s