import socket
import thread
import traceback
import string
import time
import sys

BUFFERSIZE = 4096
ESCAPE_CHARACTER = chr(4)


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

		self.received_messages = {}
		self.messages_to_send = {}

		print "-Server running."

	def accept(self):
		while True:
			clientsocket, address = self.serversocket.accept()
			print "-Connection made from",address

			if str(address) in self.clients:
				print "-- connection already exists!"
				print "-- closing connection."
				clientsocket.shutdown(socket.SHUT_RDWR)
				clientsocket.close()
			else:
				print "-- this is a new connection"
				print "-- creating new thread..."
				self.clients[str(address)] = clientsocket
				self.client_listen_threads[str(address)] = thread.start_new_thread(self.listen, tuple([str(address)]))
				self.client_transmit_threads[str(address)] = thread.start_new_thread(self.transmit, tuple([str(address)]))
				self.received_messages[str(address)] = []
				self.messages_to_send[str(address)] = []

	def transmit(self, address):
		clientsocket = self.clients[address]
		while True:
			if address not in self.messages_to_send:
				print "-missing",address
				print "-TRANSMIT THREAD FOR '"+address+"' EXITING..."
				thread.exit()
			else:
				try:
					if len(self.messages_to_send[address]) > 0:
						message = self.messages_to_send[address].pop(0) + ESCAPE_CHARACTER
						print "-Sending message: "+message[0:100]
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
				clientsocket.shutdown(socket.SHUT_RDWR)
				clientsocket.close()
				del self.clients[address]
				del self.received_messages[str(address)]
				del self.messages_to_send[str(address)]
				del clientsocket
				print "-LISTEN THREAD FOR '"+address+"' EXITING..."
				thread.exit()
			else:
				message += recv
				if message[-1] == ESCAPE_CHARACTER:
					self.received_messages[address].append(message[:-1])
					message = ""

	def sendall(self,message):
		for key in self.clients:
			self.sendto(key,message)

	def sendto(self,address,message):
		if address in self.clients:
			self.messages_to_send[address].append(message)
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




class Client(object):
	def __init__(self, host, port):
		self.buffersize = BUFFERSIZE

		print "-Connecting..."
		self.serversocket = socket.socket(
			socket.AF_INET, socket.SOCK_STREAM)
		self.serversocket.connect((host, port))
		print "-Connected."

		self.listen_thread = thread.start_new_thread(self.listen, tuple())
		self.transmit_thread = thread.start_new_thread(self.transmit, tuple())

		self.received_messages = []
		self.messages_to_send = []

	def transmit(self):
		while True:
			if len(self.messages_to_send) > 0:
				message = self.messages_to_send.pop(0) + ESCAPE_CHARACTER
				try:
					while len(message) > 0:
						sent = self.serversocket.send(message)
						message = message[sent:]
				except:
					print "-Failed to transmit message."
					print "-TRANSMIT THREAD EXITING..."
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
				thread.exit()
			else:
				#print "-recv: "+recv
				message += recv
				if message[-1] == ESCAPE_CHARACTER:
					print "-message received from client"
					self.received_messages.append(message[:-1])
					message = ""

	def send(self, message):
		self.messages_to_send.append(message)

	def close(self):
		#self.listen_thread.exit()
		self.serversocket.shutdown(socket.SHUT_RDWR)
		self.serversocket.close()

