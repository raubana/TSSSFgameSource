from ServerController import ServerController
import time

class SetupNewgameServerController(ServerController):
	def init(self):
		self.gameserver.game_started = True

		self.events = 	[
							(self.SendMessage, tuple("ADD_CHAT:SERVER:The game has begun!")),
					   		(self.Wait, tuple(0.5)),
					   		(self.SendMessage, tuple("ADD_CHAT:SERVER:Shuffling decks...")),
					   		(self.SendMessage, tuple("ALERT:remove_deck")),
							(self.Wait, tuple(0.5)),
							(self.SendMessage, tuple("ALERT:shuffle_deck")),
							(self.SetupDecks, tuple()),
							(self.Wait, tuple(0.5)),
							(self.SendMessage, tuple("ALERT:place_deck")),
							(self.Wait, tuple(1.5)),
							(self.SendMessage, tuple("ADD_CHAT:SERVER:Giving players their starting hands...")),
							(self.SendMessage, tuple("ALERT:draw_card_from_deck")),
							(self.Wait, tuple(0.1)),
							(self.SendMessage, tuple("ALERT:draw_card_from_deck")),
							(self.Wait, tuple(0.1)),
							(self.SendMessage, tuple("ALERT:draw_card_from_deck")),
							(self.Wait, tuple(0.5)),
							(self.GivePlayersStartHands, tuple()),
							(self.SendMessage, tuple("ALERT:add_card_to_hand")),
							(self.Wait, tuple(3.0)),
							(self.SendMessage, tuple("ADD_CHAT:SERVER:Drawing public goals...")),
							(self.SendMessage, tuple("ALERT:draw_card_from_deck")),
							(self.Wait, tuple(0.4)),
							(self.SendMessage, tuple("ALERT:draw_card_from_deck")),
							(self.Wait, tuple(0.4)),
							(self.SendMessage, tuple("ALERT:draw_card_from_deck")),
							(self.Wait, tuple(0.75)),
							(self.SendMessage, tuple("ALERT:add_card_to_table")),
							(self.DrawPublicGoals, tuple()),
							(self.Wait, tuple(3.0)),
							(self.SendMessage, tuple("ADD_CHAT:SERVER:Let's see who gets to go first!")),
							(self.Wait, tuple(2.0)),
							(self.PickFirstPlayer, tuple()),
							(self.SendMessage, tuple("ADD_CHAT:SERVER:This is as far as I've got with the code. You'll want to close the program now.")),
						]

		self.waiting = False
		self.wait_duration = 0
		self.wait_start_time = 0

	def update(self):
		if self.waiting:
			t = time.time()
			if t >= self.wait_duration + self.wait_start_time:
				self.waiting = False

		if not self.waiting:
			if len(self.events) > 0:
				event = self.events.pop(0)
				event[0](event[1])

	def SendMessage(self, args):
		message = args[0]
		self.gameserver.server.sendall(message)

	def Wait(self, args):
		self.waiting = True
		self.wait_duration = args[0]
		self.wait_start_time = time.time()

	def SetupDecks(self, args):
		pass

	def GivePlayersStartHand(self, args):
		pass

	def DrawPublicCards(self, args):
		pass

	def PickFirstPlayer(self, args):
		pass
