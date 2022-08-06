# ---------------------------------------------------------------------------------------------
#  Copyright (c) Akash Nag. All rights reserved.
#  Licensed under the MIT License. See LICENSE.md in the project root for license information.
# ---------------------------------------------------------------------------------------------

# This module handles all key-press and key-bindings related functions

from ash import *
from ash.utils import *

MOUSE_CLICK				= 0
MOUSE_RIGHT_CLICK		= 1
MOUSE_DOUBLE_CLICK		= 2
MOUSE_DOWN				= 3
MOUSE_UP				= 4
MOUSE_WHEEL_UP			= 5
MOUSE_WHEEL_DOWN		= 6

# <------------------ arrow symbols ----------------------->

ARROW_LEFT				= "\u2190"
ARROW_UP				= "\u2191"
ARROW_RIGHT				= "\u2192"
ARROW_DOWN				= "\u2193"

def is_window_movement_command(ch):
	if(KeyBindings.is_key(ch, "MOVE_WINDOW_LEFT") or KeyBindings.is_key(ch, "MOVE_WINDOW_RIGHT") or KeyBindings.is_key(ch, "MOVE_WINDOW_UP") or KeyBindings.is_key(ch, "MOVE_WINDOW_DOWN")):
		return True
	else:
		return False

def fn(n):
	if(n >= 1 and n <= 12): return "KEY_F(" + str(n) + ")"

def ctrlfn(n):
	if(n >= 1 and n <= 12): return "KEY_F(" + str(n+24) + ")"

class FakeKey:
	def __init__(self, keyname):
		self.keyname = "b'" + keyname + "'"

	def __str__(self):
		return self.keyname

class KeyBindings:
	@classmethod
	def get_list_of_bindings(cls):
		blist = list()
		for command, key in cls.BINDINGS.items():
			blist.append( (key[1], key[2]) )
		return sorted(blist, key = lambda x: x[1])

	@classmethod
	def is_mouse(cls, ch):
		return(True if str(curses.keyname(ch))[2:-1] == "KEY_MOUSE" else False)

	@classmethod
	def get_mouse(cls, ch):
		_, x, y, _, bstate = curses.getmouse()
		if(bstate == curses.BUTTON1_CLICKED):
			btn = MOUSE_CLICK
		elif(bstate == curses.BUTTON1_DOUBLE_CLICKED):
			btn = MOUSE_DOUBLE_CLICK
		elif(bstate == curses.BUTTON3_CLICKED):
			btn = MOUSE_RIGHT_CLICK
		elif(bstate == curses.BUTTON1_PRESSED):
			btn = MOUSE_DOWN
		elif(bstate == curses.BUTTON1_RELEASED):
			btn = MOUSE_UP
		elif(bstate == curses.BUTTON4_CLICKED):
			btn = MOUSE_WHEEL_UP
		elif(bstate == curses.BUTTON2_CLICKED):
			btn = MOUSE_WHEEL_DOWN
		else:
			btn = None
		return (btn, y, x)

	@classmethod
	def get_keyname(cls, ch):
		return str(curses.keyname(ch))[2:-1]

	@classmethod
	def get_key(cls, command):
		key = cls.BINDINGS.get(command)[0]
		if(type(key) == list):
			keyname = key[0]
		else:
			keyname = key
		return FakeKey(keyname)
	
	@classmethod
	def get_keyname(cls, key):
		key_info = cls.BINDINGS.get(key)
		if(key_info != None):
			return key_info[1]
		else:
			return "<unknown>"
	
	@classmethod
	def get_key_desc(cls, key):
		key_info = cls.BINDINGS.get(key)
		if(key_info != None):
			return key_info[2]
		else:
			return "<unavailable>"

	@classmethod
	def is_key(cls, ch, key):
		if(type(ch) == FakeKey):
			sch = str(ch)
		else:
			sch = str(curses.keyname(ch))
		key_info = cls.BINDINGS.get(key)
		if(key_info == None): return False
		key_constant = key_info[0]
		if(key_constant == None): return False
		if(type(key_constant) == str and sch == "b'" + key_constant + "'"):
			return True
		elif(type(key_constant) == list):
			mod_list = [ "b'" + item + "'" for item in key_constant ]
			if(sch in mod_list):
				return True
			else:
				return False
		else:
			return False