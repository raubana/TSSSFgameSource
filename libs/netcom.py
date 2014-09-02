from locals import*

import socket
import thread
import traceback
import string
import time
import sys

def get_this_computers_external_address():
	#I stole this code huehuehue - http://stackoverflow.com/a/9944261/2862816
	import urllib
	import re
	f = urllib.urlopen("http://www.canyouseeme.org/")
	html_doc = f.read()
	f.close()
	m = re.search('(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)',html_doc)
	return m.group(0)

def gethostname():#a simple wrapper function
	return socket.gethostname()


class Server(object):
	def __init__(self, host, port):
		print "-Starting server..."
		self.buffersize = BUFFERSIZE

		self.serversocket = socket.socket(
			socket.AF_INET, socket.SOCK_STREAM)
		self.serversocket.bind((host, port))
		self.serversocket.listen(5)

		self.accept_thread = thread.start_new_thread(self.accept, tuple([]))

		self.clients = {}
		self.client_listen_threads = {}
		self.client_transmit_threads = {}
		self.client_last_got_message = {}

		self.received_messages = {}
		self.messages_to_send = {}

		print "-Server running."

	def accept(self):
		while True:
			clientsocket, address = self.serversocket.accept()
			print "-Connection made from",address

			address = str(address)

			if str(address) in self.clients:
				print "-- connection already exists!"
				print "-- closing connection."
				#clientsocket.shutdown(socket.SHUT_RDWR)
				clientsocket.close()
			else:
				print "-- this is a new connection"
				print "-- creating new thread..."
				print clientsocket, address
				self.clients[address] = clientsocket
				self.client_listen_threads[address] = thread.start_new_thread(self.listen, tuple([str(address)]))
				self.client_transmit_threads[address] = thread.start_new_thread(self.transmit, tuple([str(address)]))
				self.received_messages[address] = []
				self.messages_to_send[address] = []
				self.client_last_got_message[address] = time.time()

	def transmit(self, address):
		clientsocket = self.clients[address]
		while True:
			time.sleep(MESSAGE_DELAY)
			if address not in self.messages_to_send:
				print "-missing",address
				print "-TRANSMIT THREAD FOR '"+address+"' EXITING..."
				thread.exit()
			else:
				try:
					if len(self.messages_to_send[address]) > 0:
						message = self.messages_to_send[address].pop(0) + ESCAPE_CHARACTER
						#print "-Sending message: "+message[0:100]
						while len(message) > 0:
							sent = clientsocket.send(message)
							message = message[sent:]
				except:
					print "-Failed to transmit message to",address
					print "-TRANSMIT THREAD FOR '"+address+"' EXITING..."
					thread.exit()

	def listen(self,address):
		clientsocket = self.clients[address]
		message = ""
		while True:
			try:
				recv = clientsocket.recv(self.buffersize)
			except:
				recv = None
			if not recv:
				print "-Connection at",address,"dropped."
				#clientsocket.shutdown(socket.SHUT_RDWR)
				clientsocket.close()
				del self.clients[address]
				del self.received_messages[address]
				del self.messages_to_send[address]
				del clientsocket
				print "-LISTEN THREAD FOR '"+address+"' EXITING..."
				thread.exit()
			else:
				self.client_last_got_message[address] = time.time()
				message += recv
				i = -min((len(ESCAPE_CHARACTER)+len(recv)),len(message))
				m2 = message[i:]
				if ESCAPE_CHARACTER in m2:
					m1 = message[:i]
					data = m2.split(ESCAPE_CHARACTER)
					m1 += data.pop(0)
					self.received_messages[address].append(str(m1))
					while len(data) > 1:
						self.received_messages[address].append(str(data.pop(0)))
					message = data.pop()

	def sendall(self,message):
		for key in self.clients:
			self.sendto(key,message)

	def sendto(self,address,message):
		if address in self.clients:
			try:
				self.messages_to_send[address].append(message)
			except:
				print "-ERROR! Attempted to add message to the buffer, but an error was raised."
		else:
			print "-Sorry, that client doesn't exist."

	def close(self):
		print "-Killing ACCEPT connection..."
		self.serversocket.close()
		print "-Killing all client connections..."
		addresses = self.clients.keys()
		for address in addresses:
			print "--"+address
			self.clients[address].close()
			del self.clients[address]
		print "-SERVER CLOSED. FECK OFF."

	def disconnect(self, address):
		print "-Killing connection with",address,"..."
		if address in self.clients:
			self.clients[address].close()
			del self.clients[address]
		else:
			print "-Sorry, that client doesn't exist."


class Client(object):
	def __init__(self, host, port):
		self.buffersize = BUFFERSIZE

		self.host = host
		self.port = port

		self.connected = False
		self.connection_status = ""

	def connect(self):
		try:
			print "-Connecting..."
			self.serversocket = socket.socket(
				socket.AF_INET, socket.SOCK_STREAM)
			self.serversocket.connect((self.host, self.port))
			print "-Connected."

			self.listen_thread = thread.start_new_thread(self.listen, tuple())
			self.transmit_thread = thread.start_new_thread(self.transmit, tuple())
			self.server_last_got_message = time.time()

			self.received_messages = []
			self.messages_to_send = []

			self.connected = True
		except Exception, e:
			print "-Failed to connect."
			self.connection_status = str(e)

	def transmit(self):
		while True:
			time.sleep(MESSAGE_DELAY)
			if len(self.messages_to_send) > 0:
				message = self.messages_to_send.pop(0) + ESCAPE_CHARACTER
				try:
					while len(message) > 0:
						sent = self.serversocket.send(message)
						message = message[sent:]
				except:
					print "-Failed to transmit message."
					print "-TRANSMIT THREAD EXITING..."
					self.connected = False
					thread.exit()

	def listen(self):
		message = ""
		while True:
			try:
				recv = self.serversocket.recv(self.buffersize)
			except:
				recv = None
			if not recv:
				print "-Connection dropped."
				self.serversocket.close()
				print "-LISTEN THREAD EXITING..."
				self.connected = False
				thread.exit()
			else:
				#print "-recv: "+recv
				self.server_last_got_message = time.time()
				message += recv
				i = -min((len(ESCAPE_CHARACTER)+len(recv)),len(message))
				m2 = message[i:]
				if ESCAPE_CHARACTER in m2:
					m1 = message[:i]
					data = m2.split(ESCAPE_CHARACTER)
					m1 += data.pop(0)
					self.received_messages.append(str(m1))
					while len(data) > 1:
						self.received_messages.append(str(data.pop(0)))
					message = data.pop()

	def send(self, message):
		self.messages_to_send.append(message)

	def close(self):
		#self.listen_thread.exit()
		#self.serversocket.shutdown(socket.SHUT_RDWR)
		self.connected = False
		self.serversocket.close()

