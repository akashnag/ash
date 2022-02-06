# ---------------------------------------------------------------------------------------------
#  Copyright (c) Akash Nag. All rights reserved.
#  Licensed under the MIT License. See LICENSE.md in the project root for license information.
# ---------------------------------------------------------------------------------------------

# This module handles all color formatting for the application

import ash
from ash.core.ashException import AshException
from ash.formatting import *

# multiplier constant for translation to/from RGB
MULTIPLIER					= 1000 / 256

# <----------------------- color formatting functions ----------------->

# sets the default color theme for ash
def get_default_colors():
	colors = dict()
	element_colors = dict()

	colors["darkgray"] = (113, 113, 113)
	colors["lightgray"] = (516, 516, 516)
	colors["dimwhite"] = (825, 825, 825)
	colors["white"] = (999, 999, 999)
	colors["red"] = (999, 0, 0)
	colors["green"] = (410, 594, 328)
	colors["blue"] = (332, 605, 832)
	colors["yellow"] = (953, 906, 246)
	colors["cyan"] = (145, 773, 914)
	colors["magenta"] = (999, 0, 999)
	colors["purple"] = (766, 520, 746)
	colors["orange"] = (801, 562, 465)

	element_colors["background"] = ("dimwhite", "darkgray")
	element_colors["editor-background"] = ("dimwhite", "darkgray")
	
	element_colors["titlebar"] = ("white", "darkgray")
	element_colors["outer-border"] = ("white", "darkgray")
	element_colors["line-number"] = ("lightgray", "darkgray")
	element_colors["highlighted-line-number"] = ("white", "darkgray")
	element_colors["selection"] = ("darkgray", "yellow")
	element_colors["highlight"] = ("darkgray", "magenta")
	element_colors["form-label"] = ("white", "darkgray")
	element_colors["formfield"] = ("cyan", "darkgray")
	element_colors["formfield-focussed"] = ("darkgray", "cyan")
	element_colors["formfield-selection-blurred"] = ("darkgray", "dimwhite")
	element_colors["inner-border"] = ("lightgray", "darkgray")
	element_colors["messagebox-border"] = ("white", "red")
	element_colors["messagebox-background"] = ("white", "red")
	element_colors["disabled"] = ("lightgray", "darkgray")
	element_colors["cursor"] = ("darkgray", "white")

	element_colors["menu-bar"] = ("darkgray", "white")
	
	element_colors["dropdown"] = ("darkgray", "white")
	element_colors["dropdown-border"] = ("darkgray", "white")
	element_colors["dropdown-disabled"] = ("lightgray", "white")
	element_colors["dropdown-selection"] = ("white", "darkgray")
	element_colors["dropdown-disabled-selection"] = ("lightgray", "darkgray")

	element_colors["popup"] = ("white", "darkgray")
	element_colors["popup-border"] = ("white", "darkgray")
	element_colors["popup-disabled"] = ("lightgray", "darkgray")
	element_colors["popup-selection"] = ("darkgray", "yellow")
	element_colors["popup-disabled-selection"] = ("white", "yellow")

	element_colors["scrollbar-buttons"] = ("white", "darkgray")
	element_colors["scrollbar-empty"] = ("white", "darkgray")
	element_colors["scrollbar-bar"] = ("white", "darkgray")

	element_colors["status-0"] = ("darkgray", "white")
	element_colors["status-1"] = ("darkgray", "white")
	element_colors["status-2"] = ("darkgray", "white")
	element_colors["status-3"] = ("darkgray", "white")
	element_colors["status-4"] = ("darkgray", "white")
	element_colors["status-5"] = ("darkgray", "white")
	element_colors["status-6"] = ("darkgray", "white")
	element_colors["status-7"] = ("darkgray", "white")
	
	element_colors["global-default"] = ("dimwhite", "darkgray")
	element_colors["global-highlighted"] = ("white", "darkgray")
	element_colors["global-keyword"] = ("blue", "darkgray")
	element_colors["global-comment"] = ("green", "darkgray")
	element_colors["global-string"] = ("orange", "darkgray")
	element_colors["global-error"] = ("red", "darkgray")
	element_colors["global-function"] = ("purple", "darkgray")
	element_colors["global-variable"] = ("dimwhite", "darkgray")
	element_colors["global-punctuation"] = ("dimwhite", "darkgray")
	element_colors["global-integer"] = ("dimwhite", "darkgray")
	element_colors["global-float"] = ("dimwhite", "darkgray")
	element_colors["global-operator"] = ("dimwhite", "darkgray")
	element_colors["global-builtin-function"] = ("cyan", "darkgray")
	element_colors["global-builtin-constant"] = ("blue", "darkgray")
	element_colors["global-namespace"] = ("dimwhite", "darkgray")
	element_colors["global-code"] = ("white", "lightgray")

	element_colors["gitstatus-A"] = ("green", "darkgray")
	element_colors["gitstatus-D"] = ("red", "darkgray")
	element_colors["gitstatus-R"] = ("yellow", "darkgray")
	element_colors["gitstatus-M"] = ("orange", "darkgray")
	element_colors["gitstatus-T"] = ("orange", "darkgray")
	element_colors["gitstatus-U"] = ("green", "darkgray")
	
	element_colors["inactive-filename-display"] = ("darkgray", "white")

	return (colors, element_colors)

# returns the index for a specified color name
def get_color_index(color_name):
	colnames = ( "darkgray", "lightgray", "dimwhite", "white", 
				 "red", "green", "blue", "yellow", "cyan", "magenta",
				 "purple", "orange" )

	try:
		return colnames.index(color_name)
	except:
		return -1

# returns the index for a specified colorable element-name
def get_element_color_index(element_name):
	element_names = ( 	"null", "background", "editor-background",
						"titlebar", "outer-border", "line-number", "highlighted-line-number",
						"selection", "highlight", "cursor",
						"form-label", "formfield", "formfield-focussed", "formfield-selection-blurred",
						"inner-border", "messagebox-border", "messagebox-background", "disabled",
						"status-0", "status-1",	"status-2", "status-3",	"status-4", "status-5",
						"status-6", "status-7", "global-default", "global-highlighted",  "global-keyword", "global-comment",
						"global-string", "global-error", "global-function", "global-variable",
						"global-punctuation", "global-integer", "global-float", "global-operator",
						"global-builtin-function", "global-builtin-constant", "global-namespace",
						"global-code", "inactive-filename-display", 
						"menu-bar", "scrollbar-buttons", "scrollbar-empty", "scrollbar-bar",
						"popup", "popup-border", "popup-disabled", "popup-selection", "popup-disabled-selection",
						"dropdown", "dropdown-border", "dropdown-disabled", "dropdown-selection", "dropdown-disabled-selection",
						"gitstatus-A", "gitstatus-D", "gitstatus-R", "gitstatus-M", "gitstatus-T", "gitstatus-U"
					)

	try:
		return element_names.index(element_name)
	except:
		return -1

# records color pairs into curses color-pair palette
def set_colors(colors, element_colors):
	supports_colors = True

	for colname, rgb in colors.items():
		index = get_color_index(colname)
		if(index < 0): continue
		try:
			curses.init_color(index, rgb[0], rgb[1], rgb[2])
		except:
			supports_colors = False
			break
		
	for elemname, pair in element_colors.items():
		index = get_element_color_index(elemname)
		fgindex = get_color_index(pair[0])
		bgindex = get_color_index(pair[1])
		if(index < 0 or fgindex < 0 or bgindex < 0): continue
		try:
			curses.init_pair(index, fgindex, bgindex)
		except:
			# if terminal does not support color remapping
			supports_colors = False
			break
			#raise(AshException(", ".join([str(index), str(fgindex), str(bgindex)])))

	return supports_colors

# retrieve a curses.color_pair() object for a given color combination
def gc(cp = "global-default"):
	return curses.color_pair(get_element_color_index(cp))