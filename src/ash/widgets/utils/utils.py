# ---------------------------------------------------------------------------------------------
#  Copyright (c) Akash Nag. All rights reserved.
#  Licensed under the MIT License. See LICENSE.md in the project root for license information.
# ---------------------------------------------------------------------------------------------

# This module handles all utility functions

from ash.widgets.utils import *

# <---------------------- key bindings --------------------------->

# check if a Ctrl+Key combination was pressed
def is_ctrl(ch, key):
	key = str(key).upper()
	sch = str(curses.keyname(ch))
	return(True if sch == "b'^" + key + "'" else False)

# check if either a Ctrl+Key or a Function-key has been pressed
def is_ctrl_or_func(ch):
	sch = str(curses.keyname(ch))
	return(True if sch.startswith("b'KEY_F(") or sch.startswith("b'^") or (sch.startswith("b'k") and sch.endswith("5'")) else False)

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