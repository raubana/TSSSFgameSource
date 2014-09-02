#!/usr/bin/env python
# -*- coding: utf-8 -*-

from ServerController import ServerController

from ..GameServer import Player
from ..locals import *

import time

class PreGameController(ServerController):
	def init(self):
		self.last_updated_playerlist = 0

	def update(self):
		t = time.time()
		if t - self.last_updated_playerlist > 1:
			self.last_updated_playerlist = t
			# Check if any players have connected
			for key in self.gameserver.server.clients.keys():
				match = False
				for player in self.gameserver.players:
					if player.address == key:
						match = True
						break
				if not match:
					#TODO: Kick them if the server is full or they're banned
					if False:
						pass
					else:
						#This player is attempting to connect, we need to receive a CONNECT request before we continue.
						pass
			# Check if any players have disconnected
			keys = self.gameserver.server.clients.keys()
			i = len(self.gameserver.players) - 1
			while i >= 0:
				player = self.gameserver.players[i]
				if player.address not in keys:
					#Player has disconnected
					print "=Player '"+player.name+"'", player.address, "has left the game."
					self.gameserver.server.sendall("ADD_CHAT:"+"Player '"+player.name+"' has left.")
					#TODO: Do proper cleanup for disconnected players.
					del self.gameserver.players[i]
					self.send_playerlist()
				i -= 1

	def read_messages(self):
		for key in self.gameserver.server.clients.keys():
			message = None
			player = None
			for pl in self.gameserver.players:
				if pl.address == key:
					player = pl
					break

			try:
				if len(self.gameserver.server.received_messages[key]) > 0:
					message = self.gameserver.server.received_messages[key].pop(0)
			except:
				print "= FAILED TO POP AT KEY:",key

			if message != None:
				if message == PING_MESSAGE:
					self.gameserver.server.sendto(key,PONG_MESSAGE)
				elif message.startswith("CONNECT:"):
					#We get the clients name now and add them to the game.
					#TODO: Kick the client if their name sucks.
					if False:
						pass
					else:
						name = message[len("CONNECT:"):]
						self.gameserver.players.append(Player(key, name))
						self.gameserver.server.sendto(key,"CONNECTED")
						print "=Player '"+name+"'", key, "has joined the game."
						self.gameserver.server.sendall("ADD_CHAT:"+"Player '"+name+"' has joined.")
						self.send_playerlist()
				elif message.startswith("CHAT:"):
					if not player:
						name = "UNKNOWN"
					else:
						name = player.name
					chat = message[len("CHAT:"):]
					self.gameserver.server.sendall("ADD_CHAT:"+name+": "+chat)
				elif message == "READY":
					if player.is_ready != True:
						player.is_ready = True
						self.gameserver.server.sendall("ALERT_READY")
						self.send_playerlist()
				elif message == "NOT_READY":
					if player.is_ready != False:
						player.is_ready = False
						self.gameserver.server.sendall("ALERT_NOT_READY")
						self.send_playerlist()

	def check_player_status(self):
		# This function is to check that players are still connected, otherwise it kicks them after no response.
		t = time.time()
		player_list = list(self.gameserver.players)
		for player in player_list:
			pa = player.address
			pn = player.name

			kick_em = False
			# First we check if the player is even still in the server's client listing.
			if pa in self.gameserver.server.clients:
				#Next we check when we last received a message from that client.
				try:
					lgm = self.gameserver.server.client_last_got_message[pa]
					dif = t - lgm
					if dif >= PING_FREQUENCY:
						if not player.is_pinged:
							player.is_pinged = True
							self.gameserver.server.sendto(pa,PING_MESSAGE)
						else:
							# This means the player was already sent a 'ping', and we're waiting for a 'pong'
							if dif >= PING_FREQUENCY + TIMEOUT_TIME:
								#This player has timed out, so we must kick them.
								print "= Client '"+pn+"' has timed-out from '"+pa+"'"
								kick_em = True
					else:
						# This player is likely still connected.
						player.is_pinged = False
				except:
					print "= FAILED TO CHECK ON AND/OR PING PLAYER '"+pn+"' AT '"+pa+"'"
			else:
				print "= Client '"+pn+"' has disconnected from '"+pa+"'"
				kick_em = True
			if kick_em:
				print "= Player '"+pn+"' has been kicked."
				self.gameserver.server.disconnect(pa)
				self.gameserver.players.remove(player)
				self.send_playerlist()
				#TODO: send message to remaining clients to let them know about the updated player list.

	def send_playerlist(self):
		self.players_ready = 0
		s = "PLAYERLIST:"
		i = 0
		while i < len(self.gameserver.players):
			if self.gameserver.players[i].is_ready:
				s += "☑ "
				self.gameserver.players_ready += 1
			else:
				s += "☐ "
			s += self.gameserver.players[i].name
			if i != len(self.gameserver.players)-1:
				s += ","
			i += 1
		self.gameserver.server.sendall(s)