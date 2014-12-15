#This file is made for parsing the 'your_deck.txt' file.
import os

def check_function_name_is_legal(name):
	if name == "":
		raise SyntaxError("A function can't be nameless")
	if name[0].isdigit():
		raise SyntaxError("A function can't begin with a number")
	for ch in name:
		if not ch.isalnum() and ch != "_":
			raise SyntaxError("A function can't have the character '" + ch + "'")


def split_args(arg_line):
	args = []
	arg_toggle = False
	expect_comma = False
	current_arg = None
	i = 0
	while i < len(arg_line):
		ch = arg_line[i]
		if ch.isalnum() or ch != "_":
			if current_arg == None:
				current_arg = ""
			current_arg += ch
		elif ch == ",":
			if current_arg != None:
				if expect_comma:
					expect_comma = False
				else:
					raise SyntaxError("Two consecutive commas without an arg in between")
				args.append(str(current_arg))
				current_arg = None
				expect_comma = False
			else:
				current_arg += ","
		else:
			raise SyntaxError("Don't know why this symbol is here... '" + ch + "'")
		i += 1
	if current_arg != None:
		args.append(current_arg)
	return args


def split_line(line):
	line = line.strip()# we remove whitespace
	if len(line) == 0 or line[0] == "#":
		return None
	first_par_index = line.find("(")
	if first_par_index == -1:
		fnc = line
		args = []
		check_function_name_is_legal(fnc)
	else:
		fnc = line[:first_par_index]
		check_function_name_is_legal(fnc)
		arg_line = line[first_par_index:]
		if arg_line[-1] != ")":
			raise
		arg_line = arg_line[1:-1]# we remove the parentheses
		args = split_args(arg_line)
	return (fnc,args)


class CustomDeck(object):
	def __init__(self):
		self.list = []

	def follow_instructions(self, instr):
		self.list = []
		legal_fncs = 	{
							"add_all_default": self._add_all_default,
					  		"add_all_cards": self._add_all_cards,
					  		"add_all": self._add_all,
					 		"add": self._add,
							"remove": self._remove,
							"replace": self._replace
						}
		lines = instr.split("\n")
		i = 0
		while i < len(lines):
			line = lines[i]
			try:
				results = split_line(line)
				if results == None:
					pass
				else:
					fnc = results[0]
					args = results[1]
					if fnc not in legal_fncs:
						raise NameError("The function '"+fnc+"' is not allowed or doesn't exist.")
					legal_fncs[fnc](args)
			except Exception, e:
				print "Line "+str(i+1)+": "+str(e)
			i += 1

	def _add(self, args):
		if len(args) != 1:
			raise TypeError("'add' needs exactly 1 argument")
		if not (args[0].endswith(".tsssf") or args[0].endswith(".tsf")):
			raise RuntimeError("'"+args[0]+"' is not of an appropriate file type")
		if args[0] in self.list:
			raise RuntimeError("'"+args[0]+"' is already in the list")
		if "R:"+args[0] in self.list:
			raise RuntimeError("A replacement for '"+args[0]+"' is already in the list")
		works = False
		files = os.listdir("data/default_cards")
		if args[0] in files:
			works = True
		else:
			files = os.listdir("cards")
			if args[0] in files:
				works = True
		if works:
			self.list.append(args[0])
		else:
			raise LookupError("The file '"+args[0]+"' doesn't exists")

	def _add_all_default(self, args):
		if len(args) != 0:
			raise TypeError("'add_all_default' doesn't take any arguments")
		files = os.listdir("data/default_cards")
		for file in files:
			self._add([file])

	def _add_all_cards(self, args):
		if len(args) != 0:
			raise TypeError("'add_all_cards' doesn't take any arguments")
		files = os.listdir("cards")
		for file in files:
			self._add([file])

	def _add_all(self, args):
		if len(args) != 0:
			raise TypeError("'add_all' doesn't take any arguments")
		self._add_all_default([])
		self._add_all_cards([])

	def _remove(self, args):
		if len(args) != 1:
			raise TypeError("'add' needs exactly 1 argument")
		if not (args[0].endswith(".tsssf") or args[0].endswith(".tsf")):
			raise RuntimeError("'"+args[0]+"' is not of an appropriate file type")
		if args[0] not in self.list:
			raise LookupError("'"+args[0]+"' is not in the list")
		self.list.remove(args[0])

	def _replace(self, args):
		if len(args) != 1:
			raise TypeError("'replace' needs exactly 1 argument")
		if not (args[0].endswith(".tsssf") or args[0].endswith(".tsf")):
			raise RuntimeError("'"+args[0]+"' is not of an appropriate file type")
		if "R:"+args[0] in self.list:
			raise RuntimeError("A replacement for '"+args[0]+"' is already in the list")
		if args[0] not in self.list:
			raise RuntimeError("The card to replace '"+args[0]+"' isn't in the list")
		files = os.listdir("data/default_cards")
		if args[0] not in files:
			raise LookupError("The file '"+args[0]+"' doesn't exists")
		files = os.listdir("cards")
		if args[0] not in files:
			raise LookupError("The custom file '"+args[0]+"' doesn't exists")
		self.list.remove(args[0])
		self.list.append("R:"+args[0])




