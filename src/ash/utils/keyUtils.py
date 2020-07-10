# ---------------------------------------------------------------------------------------------
#  Copyright (c) Akash Nag. All rights reserved.
#  Licensed under the MIT License. See LICENSE.md in the project root for license information.
# ---------------------------------------------------------------------------------------------

# This module handles all key-press and key-bindings related functions

from ash.utils import *

ASH_KEY_BINDINGS = [
	("GROUP:", "GENERAL COMMANDS"),
	("------", "--------------------------------------------"),
	("Ctrl + Q", "Close the active window"),
	("Ctrl + @", "Discard any unsaved changes and close ash"),
	("F1", "Activate the 1st editor in the layout"),
	("F2", "Activate the 2nd editor in the layout"),
	("F3", "Activate the 3rd editor in the layout"),
	("F4", "Activate the 4th editor in the layout"),
	("F5", "Activate the 5th editor in the layout"),
	("F6", "Activate the 6th editor in the layout"),
	("F11", "Resize window"),
	("F12", "Show this help"),
	("", ""),			# blank line
	
]

def get_ash_key_bindings():
	return ASH_KEY_BINDINGS

# check if Caps Lock is on/off
def is_capslock_on():
	x = int(subprocess.getoutput("xset q | grep LED")[65])
	return(True if x==1 else False)

# check if a Ctrl+Key combination was pressed
def is_ctrl(ch, key):
	key = str(key).upper()
	sch = str(curses.keyname(ch))
	return(True if sch == "b'^" + key + "'" else False)

# check if either a Ctrl+Key or a Function-key has been pressed
def is_ctrl_or_func(ch):
	sch = str(curses.keyname(ch))
	return(True if sch.startswith("b'KEY_F(") or sch.startswith("b'^") or (sch.startswith("b'k") and sch.endswith("5'")) else False)

# check if a particular function key has been pressed
def is_func(ch, k=None):
	sch = str(curses.keyname(ch))
	if(k == None):
		return(True if sch.startswith("b'KEY_F(") else False)
	else:
		return(True if sch == "b'KEY_F(" + str(k) + ")'" else False)

def get_func_key(ch):
	if(not is_func(ch)):
		return None
	else:
		sch = str(curses.keyname(ch))
		if(sch[9] == ")"):
			return int(sch[8])
		else:
			return int(sch[8:10])

# check if Enter or Ctrl+J has been pressed
def is_newline(ch):
	return (ch == curses.KEY_ENTER or is_ctrl(ch, "J"))

# check if Tab or Ctrl+I has been pressed
def is_tab(ch):
	return (ch == curses.KEY_STAB or is_ctrl(ch, "I"))

# check if Ctrl+Arrow has been pressed
def is_ctrl_arrow(ch, arrow = None):
	sch = str(curses.keyname(ch))
	if(arrow == None):
		return (True if (sch == "b'kUP5'" or sch == "b'kDN5'" or sch == "b'kLFT5'" or sch == "b'kRIT5'") else False)
	else:
		sarrow = str(arrow).upper()
		
		if(sch == "b'kUP5'" and sarrow == "UP"):
			return True
		elif(sch == "b'kDN5'" and sarrow == "DOWN"):
			return True
		elif(sch == "b'kLFT5'" and sarrow == "LEFT"):
			return True
		elif(sch == "b'kRIT5'" and sarrow == "RIGHT"):
			return True
		else:
			return False

def is_keyname(ch, name):
	sch = str(curses.keyname(ch))
	if(sch == "b'k" + name + "'"):
		return True
	else:
		return False