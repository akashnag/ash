# ---------------------------------------------------------------------------------------------
#  Copyright (c) Akash Nag. All rights reserved.
#  Licensed under the MIT License. See LICENSE.md in the project root for license information.
# ---------------------------------------------------------------------------------------------

# This module handles all color formatting for the application

from ash.formatting import *
from ash.core.logger import *

import os

# name of the config file
CONFIG_FILE					= os.path.expanduser("~/.ashrc")
MULTIPLIER					= 3.90625

# <----------------------- color formatting functions ----------------->
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
	
	element_colors["titlebar"] = ("white", "darkgray")
	element_colors["outer-border"] = ("white", "darkgray")
	element_colors["line-number"] = ("lightgray", "darkgray")
	element_colors["highlighted-line-number"] = ("white", "darkgray")
	element_colors["selection"] = ("darkgray", "yellow")
	element_colors["formfield"] = ("cyan", "darkgray")
	element_colors["formfield-focussed"] = ("darkgray", "cyan")
	element_colors["formfield-selection-blurred"] = ("darkgray", "dimwhite")
	element_colors["inner-border"] = ("lightgray", "darkgray")
	element_colors["messagebox-border"] = ("white", "red")
	element_colors["messagebox-background"] = ("white", "red")
	element_colors["disabled"] = ("lightgray", "darkgray")
	element_colors["cursor"] = ("darkgray", "white")

	element_colors["status-0"] = ("darkgray", "white")
	element_colors["status-1"] = ("darkgray", "white")
	element_colors["status-2"] = ("darkgray", "white")
	element_colors["status-3"] = ("darkgray", "white")
	element_colors["status-4"] = ("darkgray", "white")
	element_colors["status-5"] = ("darkgray", "white")
	element_colors["status-6"] = ("darkgray", "white")
	element_colors["status-7"] = ("darkgray", "white")
	
	element_colors["global-default"] = ("dimwhite", "darkgray")
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
	
	return (colors, element_colors)

def get_color_index(color_name):
	colnames = ( "darkgray", "lightgray", "dimwhite", "white", 
				 "red", "green", "blue", "yellow", "cyan", "magenta",
				 "purple", "orange" )

	try:
		return colnames.index(color_name)
	except:
		return -1

def get_element_color_index(element_name):
	element_names = ( 	"null",
						"titlebar", "outer-border", "line-number", "highlighted-line-number",
						"selection", "formfield", "formfield-focussed", "formfield-selection-blurred",
						"inner-border", "messagebox-border", "messagebox-background", "disabled", "cursor",
						"status-0", "status-1",	"status-2", "status-3",	"status-4", "status-5",
						"status-6", "status-7", "global-default", "global-keyword", "global-comment",
						"global-string", "global-error", "global-function", "global-variable",
						"global-punctuation", "global-integer", "global-float", "global-operator",
						"global-builtin-function", "global-builtin-constant", "global-namespace"
					) 

	try:
		return element_names.index(element_name)
	except:
		return -1

def write_to_config(colors, element_colors):
	configFile = open(CONFIG_FILE, "wt")
	for name, rgb in colors.items():
		configFile.write("color-" + name + " = rgb(" + str(int(rgb[0] // MULTIPLIER)) + ", " + str(int(rgb[1] // MULTIPLIER)) + ", " + str(int(rgb[2] // MULTIPLIER)) + ")\n")
	for name, pair in element_colors.items():
		configFile.write("color-" + name + " = (" + pair[0] + ", " + pair[1] + ")\n")
	configFile.close()

def load_config(colors = None, element_colors = None):
	if(not os.path.isfile(CONFIG_FILE)):
		return (colors, element_colors)
	
	if(colors == None): colors = dict()
	if(element_colors == None): element_colors = dict()

	configFile = open(CONFIG_FILE, "rt")
	config = configFile.read().splitlines()
	configFile.close()

	for line in config:
		# format = magenta=rgb(113,154,132)
		line = line.strip().lower().replace(" ", "")
		pos1 = line.find("=rgb(")
		pos2 = line.find("=(")

		if(not line.endswith(")") or not line.startswith("color-")): continue
		if(pos1 == -1 and pos2 == -1): continue

		if(pos1 > -1):
			triplet = line[pos1+5:-1].split(",")
			if(len(triplet) != 3): continue
			rgb = ( round(int(triplet[0]) * MULTIPLIER), round(int(triplet[1]) * MULTIPLIER), round(int(triplet[2]) * MULTIPLIER) )
			colname = line[6:pos1]
			colors[colname] = rgb
		elif(pos2 > -1):
			colname = line[6:pos2]
			pair = line[pos2+2:-1].split(",")
			if(len(pair) != 2): continue
			element_colors[colname] = (pair[0], pair[1])

	return (colors, element_colors)

def init_colors():
	colors, element_colors = get_default_colors()

	if(not os.path.isfile(CONFIG_FILE)):
		write_to_config(colors, element_colors)
		set_colors(colors, element_colors)
	else:
		colors, element_colors = load_config(colors, element_colors)
		set_colors(colors, element_colors)

def set_colors(colors, element_colors):
	for colname, rgb in colors.items():
		index = get_color_index(colname)
		if(index < 0): continue
		curses.init_color(index, rgb[0], rgb[1], rgb[2])
		
	for elemname, pair in element_colors.items():
		index = get_element_color_index(elemname)
		fgindex = get_color_index(pair[0])
		bgindex = get_color_index(pair[1])
		if(index < 0 or fgindex < 0 or bgindex < 0): continue
		try:
			curses.init_pair(index, fgindex, bgindex)
		except:
			raise(Exception(str(index), str(fgindex), str(bgindex)))

# retrieve a curses.color_pair() object for a given color combination
def gc(cp = "global-default"):
	return curses.color_pair(get_element_color_index(cp))