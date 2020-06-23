# ---------------------------------------------------------------------------------------------
#  Copyright (c) Akash Nag. All rights reserved.
#  Licensed under the MIT License. See LICENSE.md in the project root for license information.
# ---------------------------------------------------------------------------------------------

# This module handles all utility functions

from ash.widgets.utils import *

# <---------------------- key bindings --------------------------->

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

# <------------------------- other functions ---------------------->


# check if selection-start is before selection-end or vice-versa
# i.e. check if selection is forwards from the cursor, or backwards
def is_start_before_end(start, end):
	if(start.y == end.y and start.x < end.x): return True
	if(start.y < end.y): return True
	return False


def get_center_coords(app, elem_height, elem_width):
	return ((app.screen_height - elem_height) // 2, (app.screen_width - elem_width) // 2)

def beep():
	curses.beep()

def get_horizontal_cursor_position(text, curpos, tab_size):
	ptext = text[0:curpos]
	x = 0
	
	for c in ptext:
		if(c == "\t"):
			x += (tab_size - (x % tab_size))
		else:
			x += 1

	return x

def replace_tabs(text, tab_size):
	ptext = copy.copy(text)
	rtext = ""
	x = 0
	
	for c in ptext:
		if(c == "\t"):
			delta = (tab_size - (x % tab_size))
			x += delta
			rtext += (" " * delta)
		else:
			x += 1
			rtext += c

	return rtext