# ---------------------------------------------------------------------------------------------
#  Copyright (c) Akash Nag. All rights reserved.
#  Licensed under the MIT License. See LICENSE.md in the project root for license information.
# ---------------------------------------------------------------------------------------------

# This module handles all key-press and key-bindings related functions

from ash.utils import *

ARROW_LEFT		= "\u2190"
ARROW_UP		= "\u2191"
ARROW_RIGHT		= "\u2192"
ARROW_DOWN		= "\u2193"

ASH_KEY_BINDINGS = [
	("GROUP:", "GENERAL COMMANDS"),
	("------", "--------------------------------------------"),
	("Ctrl + Q", "Close the active window"),
	("Ctrl + @", "Discard any unsaved changes and close ash"),
	("Tab", "Moves focus to the next element in the active window"),
	("Shift + Tab", "Moves focus to the previous element in the active window"),
	("Space", "Checks/Unchecks selected checkbox"),
	("Enter", "Saves changes and closes the active dialog box"),
	("Ctrl + N", "Opens a new blank buffer for editing"),
	("Ctrl + O", "Shows the File-Open window"),
	(f"{ARROW_UP} {ARROW_DOWN}", "Changes the selected item in a list"),
	(f"Ctrl + {ARROW_LEFT} {ARROW_UP} {ARROW_DOWN} {ARROW_RIGHT}", "Moves the active window around"),
	(f"{ARROW_LEFT} {ARROW_RIGHT}", "Moves the cursor in a textfield"),
	("Del", "Deletes the character under the cursor"),
	("Backspace", "Deletes the character to the left of the cursor"),
	("Ctrl + L", "Opens the Layout switcher window"),
	("Ctrl + E", "Opens the project explorer (if in directory mode)"),
	("F1", "Activate the 1st editor in the layout"),
	("F2", "Activate the 2nd editor in the layout"),
	("F3", "Activate the 3rd editor in the layout"),
	("F4", "Activate the 4th editor in the layout"),
	("F5", "Activate the 5th editor in the layout"),
	("F6", "Activate the 6th editor in the layout"),
	("F11", "Resize window"),
	("F12", "Shows the list of recently opened files"),
	("Ctrl + F1", "Show this help"),	
	("", ""),			# blank line
	
	("GROUP:", "PROJECT EXPLORER"),
	("------", "--------------------------------------------"),
	("Ctrl + R", "Refresh the directory tree"),
	("Ctrl + N", "Create a new file under the selected directory"),
	("Ctrl + D", "Create a new directory under the selected directory"),
	("+", "Collapse the selected directory"),
	("-", "Expand the selected directory"),
	("F2", "Rename the selected file/directory"),
	("Del", "Move the selected file/directory to the trash/bin"),
	("", ""),			# blank line

	("GROUP:", "EDITOR COMMANDS"),
	("------", "--------------------------------------------"),
	(f"{ARROW_LEFT} {ARROW_UP} {ARROW_DOWN} {ARROW_RIGHT}", "Moves the cursor"),
	(f"Shift + {ARROW_LEFT} {ARROW_UP} {ARROW_DOWN} {ARROW_RIGHT}", "Select text"),
	("Home", "Move cursor to the beginning of the current line"),
	("End", "Move cursor to the end of the current line"),
	("Ctrl + Home", "Move cursor to the beginning of the current document"),
	("Ctrl + End", "Move cursor to the end of the current document"),
	("Shift + Home", "Selects up to the beginning of the current line"),
	("Shift + End", "Selects up to the end of the current line"),
	("PgUp", "Moves the cursor up one screenful at a time"),
	("PgDown", "Moves the cursor down one screenful at a time"),
	("Shift + PgUp", "Selects text upwards one screenful at a time"),
	("Shift + PgDown", "Selects text downwards one screenful at a time"),
	("Ctrl + A", "Selects the entire document"),

	("Del", "Deletes the character under the cursor"),
	("Backspace", "Deletes the character to the left of the cursor"),

	("Ctrl + S", "Save"),
	("Ctrl + W", "Save and close active editor"),
	("Ctrl + X", "Cut"),
	("Ctrl + C", "Copy"),
	("Ctrl + V", "Paste"),
	("Ctrl + Z", "Undo"),
	("Ctrl + Y", "Redo"),
	("Ctrl + P", "Opens the preferences window"),
	("Ctrl + G", "Opens the Go-To-Line window"),
	("Ctrl + F", "Opens the find window"),
	("Ctrl + H", "Opens the find and replace window"),
	("F9", "Save As"),
	("Ctrl + F2", "Convert all Unicode escape sequences to  Unicode characters"),
	("", ""),			# blank line

	("Website:", "https://akashnag.github.io/ash")
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

def is_ctrl_and_func(ch, k = None):
	sch = str(curses.keyname(ch))
	if(k == None):
		return(True if sch.startswith("b'KEY_F(") else False)
	else:
		return(True if sch == "b'KEY_F(" + str(int(k)+24) + ")'" else False)

# returns which function-key was pressed as an integer
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

# generic function to check the keyname of a pressed key
def is_keyname(ch, name):
	sch = str(curses.keyname(ch))
	if(sch == "b'k" + name + "'"):
		return True
	else:
		return False