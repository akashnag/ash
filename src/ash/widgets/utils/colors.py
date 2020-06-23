# ---------------------------------------------------------------------------------------------
#  Copyright (c) Akash Nag. All rights reserved.
#  Licensed under the MIT License. See LICENSE.md in the project root for license information.
# ---------------------------------------------------------------------------------------------

# This module handles all color formatting for the application

from ash.widgets.utils import *

# list of color combinations
COLOR_DIMWHITE_ON_DARKGRAY	= 1
COLOR_WHITE_ON_DARKGRAY		= 2
COLOR_WHITE_ON_LIGHTGRAY	= 3
COLOR_WHITE_ON_BLUE			= 4
COLOR_BLUE_ON_DARKGRAY		= 5
COLOR_GREEN_ON_DARKGRAY		= 6
COLOR_LIGHTGRAY_ON_DARKGRAY	= 7
COLOR_YELLOW_ON_DARKGRAY	= 8
COLOR_RED_ON_DARKGRAY		= 9
COLOR_DARKGRAY_ON_YELLOW	= 10
COLOR_WHITE_ON_RED			= 11
COLOR_DARKGRAY_ON_DIMWHITE	= 12
COLOR_DARKGRAY_ON_WHITE		= 13
COLOR_DARKGRAY_ON_BLUE		= 14

# color aliases
COLOR_DARKGRAY 						= curses.COLOR_BLACK
COLOR_WHITE 						= curses.COLOR_WHITE
COLOR_RED 							= curses.COLOR_RED
COLOR_GREEN 						= curses.COLOR_GREEN
COLOR_BLUE 							= curses.COLOR_BLUE
COLOR_YELLOW 						= curses.COLOR_YELLOW
COLOR_LIGHTGRAY 					= curses.COLOR_MAGENTA
COLOR_DIMWHITE 						= curses.COLOR_CYAN

# element color aliases
COLOR_DEFAULT 						= COLOR_DIMWHITE_ON_DARKGRAY
COLOR_TITLEBAR						= COLOR_WHITE_ON_DARKGRAY
COLOR_BORDER						= COLOR_WHITE_ON_DARKGRAY
COLOR_DIALOG_PROMPT					= COLOR_WHITE_ON_DARKGRAY
COLOR_STATUSBAR						= COLOR_DARKGRAY_ON_WHITE
COLOR_KEYWORD						= COLOR_BLUE_ON_DARKGRAY
COLOR_COMMENT						= COLOR_GREEN_ON_DARKGRAY
COLOR_LINENUMBER					= COLOR_LIGHTGRAY_ON_DARKGRAY
COLOR_HIGHLIGHTED_LINENUMBER		= COLOR_YELLOW_ON_DARKGRAY
COLOR_STRING						= COLOR_YELLOW_ON_DARKGRAY
COLOR_ERROR							= COLOR_RED_ON_DARKGRAY
COLOR_SELECTION						= COLOR_DARKGRAY_ON_YELLOW
COLOR_FORMFIELD						= COLOR_BLUE_ON_DARKGRAY
COLOR_FORMFIELD_FOCUSSED			= COLOR_DARKGRAY_ON_BLUE
COLOR_FORMFIELD_SELECTED_BLURRED	= COLOR_DARKGRAY_ON_DIMWHITE
COLOR_MSGBOX						= COLOR_WHITE_ON_RED
COLOR_DIVISION						= COLOR_LIGHTGRAY_ON_DARKGRAY

# <----------------------- color formatting functions ----------------->

# initializes the color palette and color combinations
def init_colors():
	curses.init_color(0, 140, 140, 140)
		
	curses.init_color(curses.COLOR_BLACK, 140, 140, 140)		# dark gray
	curses.init_color(curses.COLOR_WHITE, 999, 999, 999)		# bright white
	curses.init_color(curses.COLOR_RED, 999, 0, 0)
	curses.init_color(curses.COLOR_GREEN, 0, 999, 0)
	curses.init_color(curses.COLOR_BLUE, 0, 700, 999)			# sweet blue
	curses.init_color(curses.COLOR_YELLOW, 999, 999, 0)
	curses.init_color(COLOR_LIGHTGRAY, 426, 426, 426)
	curses.init_color(COLOR_DIMWHITE, 855, 855, 855)
	
	curses.init_pair(COLOR_DIMWHITE_ON_DARKGRAY, COLOR_DIMWHITE, COLOR_DARKGRAY)
	curses.init_pair(COLOR_WHITE_ON_DARKGRAY, COLOR_WHITE, COLOR_DARKGRAY)
	curses.init_pair(COLOR_WHITE_ON_LIGHTGRAY, COLOR_WHITE, COLOR_LIGHTGRAY)
	curses.init_pair(COLOR_WHITE_ON_BLUE, COLOR_WHITE, COLOR_BLUE)
	curses.init_pair(COLOR_BLUE_ON_DARKGRAY, COLOR_BLUE, COLOR_DARKGRAY)
	curses.init_pair(COLOR_GREEN_ON_DARKGRAY, COLOR_GREEN, COLOR_DARKGRAY)
	curses.init_pair(COLOR_LIGHTGRAY_ON_DARKGRAY, COLOR_LIGHTGRAY, COLOR_DARKGRAY)
	curses.init_pair(COLOR_YELLOW_ON_DARKGRAY, COLOR_YELLOW, COLOR_DARKGRAY)
	curses.init_pair(COLOR_RED_ON_DARKGRAY, COLOR_RED, COLOR_DARKGRAY)
	curses.init_pair(COLOR_DARKGRAY_ON_YELLOW, COLOR_DARKGRAY, COLOR_YELLOW)
	curses.init_pair(COLOR_WHITE_ON_RED, COLOR_WHITE, COLOR_RED)
	curses.init_pair(COLOR_DARKGRAY_ON_DIMWHITE, COLOR_DARKGRAY, COLOR_DIMWHITE)
	curses.init_pair(COLOR_DARKGRAY_ON_WHITE, COLOR_DARKGRAY, COLOR_WHITE)
	curses.init_pair(COLOR_DARKGRAY_ON_BLUE, COLOR_DARKGRAY, COLOR_BLUE)

# retrieve a curses.color_pair() object for a given color combination
def gc(cp = COLOR_DEFAULT):
	return curses.color_pair(cp)
