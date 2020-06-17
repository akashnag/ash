# ---------------------------------------------------------------------------------------------
#  Copyright (c) Akash Nag. All rights reserved.
#  Licensed under the MIT License. See LICENSE.md in the project root for license information.
# ---------------------------------------------------------------------------------------------

# This module handles all text and color formatting for the application

from ash.widgets.utils import *
from datetime import datetime

# list of color combinations
COLOR_WHITE_ON_BLACK 	= 1
COLOR_WHITE_ON_RED 		= 2
COLOR_WHITE_ON_GREEN 	= 3
COLOR_RED_ON_BLACK 		= 4
COLOR_GREEN_ON_BLACK 	= 5
COLOR_YELLOW_ON_BLACK 	= 6
COLOR_BLACK_ON_YELLOW 	= 7
COLOR_BLACK_ON_WHITE	= 8
COLOR_WHITE_ON_BLUE		= 9
COLOR_BLUE_ON_BLACK		= 10
COLOR_GRAY_ON_BLACK		= 11
COLOR_DIMWHITE_ON_BLACK	= 12

# <----------------------- color formatting functions ----------------->

# initializes the color palette and color combinations
def init_colors():
	curses.init_color(0, 0, 0, 0)

	curses.init_color(curses.COLOR_BLACK, 0, 0, 0)
	curses.init_color(curses.COLOR_WHITE, 999, 999, 999)
	curses.init_color(curses.COLOR_RED, 999, 0, 0)
	curses.init_color(curses.COLOR_GREEN, 0, 999, 0)
	curses.init_color(curses.COLOR_BLUE, 0, 478, 796)
	curses.init_color(curses.COLOR_YELLOW, 999, 999, 0)
	
	# different color mapping
	curses.init_color(curses.COLOR_MAGENTA, 426, 426, 426)		# light gray
	curses.init_color(curses.COLOR_CYAN, 856, 856, 856)		# dim white
	curses.init_pair(COLOR_GRAY_ON_BLACK, curses.COLOR_MAGENTA, curses.COLOR_BLACK)
	curses.init_pair(COLOR_DIMWHITE_ON_BLACK, curses.COLOR_CYAN, curses.COLOR_BLACK)
	# -------------------------

	curses.init_pair(COLOR_WHITE_ON_BLACK, curses.COLOR_WHITE, curses.COLOR_BLACK)
	curses.init_pair(COLOR_WHITE_ON_RED, curses.COLOR_WHITE, curses.COLOR_RED)
	curses.init_pair(COLOR_WHITE_ON_GREEN, curses.COLOR_WHITE, curses.COLOR_GREEN)
	curses.init_pair(COLOR_RED_ON_BLACK, curses.COLOR_RED, curses.COLOR_BLACK)
	curses.init_pair(COLOR_GREEN_ON_BLACK, curses.COLOR_GREEN, curses.COLOR_BLACK)
	curses.init_pair(COLOR_YELLOW_ON_BLACK, curses.COLOR_YELLOW, curses.COLOR_BLACK)
	curses.init_pair(COLOR_BLACK_ON_YELLOW, curses.COLOR_BLACK, curses.COLOR_YELLOW)
	curses.init_pair(COLOR_BLACK_ON_WHITE, curses.COLOR_BLACK, curses.COLOR_WHITE)
	curses.init_pair(COLOR_WHITE_ON_BLUE, curses.COLOR_WHITE, curses.COLOR_BLUE)
	curses.init_pair(COLOR_BLUE_ON_BLACK, curses.COLOR_BLUE, curses.COLOR_BLACK)

# retrieve a curses.color_pair() object for a given color combination
def gc(cp = COLOR_WHITE_ON_BLACK):
	return curses.color_pair(cp)

# <----------------------- string formatting functions ----------------->

# right-align a given string
def pad_left_str(data, width):
	sdata = str(data)
	n = len(sdata)
	if(n < width):
		return (" " * (width-n)) + sdata
	else:
		return sdata

# left-align a given string
def pad_right_str(data, width):
	sdata = str(data)
	n = len(sdata)
	if(n < width):
		return sdata + (" " * (width-n))
	else:
		return sdata

# center align a given string
def pad_center_str(str, maxlen):
	if(len(str) >= maxlen):
		return str
	else:
		pad = (maxlen - len(str)) // 2
		return (" " * pad) + str + (" " * pad)

# chop off a string if it exceeds maxlen and end it with "..."
def pad_str_max(data, maxlen):
	n = len(data)
	if(n <= maxlen):
		return data
	else:
		return data[0:maxlen-3] + "..."