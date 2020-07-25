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
	BINDINGS = {
		"CLOSE_WINDOW" 					: ["^Q", "Ctrl+Q", "Close the active window"],
		"FORCE_QUIT"					: ["^@", "Ctrl+@", "Discard all unsaved changes and quit ash"],
		"CANCEL_OPERATION"				: ["^C", "Ctrl+C", "Cancel ongoing operation if any"],
		"FOCUS_NEXT"					: ["^I", "Tab/Ctrl+I", "Switch focus to the next element in the active window"],
		"FOCUS_PREVIOUS"				: ["KEY_BTAB", "Shift+Tab", "Switch focus to the previous element in the active window"],
		"CHANGE_VALUE"					: [" ", "Space", "Change the selected item / toggle checkbox"],
		"SAVE_AND_CLOSE_WINDOW"			: [[ "^W", "^J", "KEY_ENTER" ], "Ctrl+W", "Save changes and close the active window"],
		"NEW_BUFFER"					: ["^N", "Ctrl+N", "Open a new buffer for editing"],
		"OPEN_FILE"						: ["^O", "Ctrl+O", "Open a file/directory"],
		
		"LIST_MOVE_SELECTION_UP"		: ["KEY_UP", ARROW_UP, "Move selection up in a list"],
		"LIST_MOVE_SELECTION_DOWN"		: ["KEY_DOWN", ARROW_DOWN, "Move selection down in a list"],
		"LIST_MOVE_SELECTION_NEXT"		: ["KEY_RIGHT", ARROW_RIGHT, "Open the next menu"],
		"LIST_MOVE_SELECTION_PREVIOUS"	: ["KEY_LEFT", ARROW_LEFT, "Open the previous menu"],
		"LIST_MOVE_TO_PREVIOUS_PAGE"	: ["KEY_PPAGE", "PgUp", "Move selection up one page"],
		"LIST_MOVE_TO_NEXT_PAGE"		: ["KEY_NPAGE", "PgDown", "Move selection down one page"],
		"LIST_MAKE_SELECTION"			: [[ "^J", "KEY_ENTER" ], "Ctrl+J/Enter", "Select the currently selected item"],
		
		"MOVE_WINDOW_LEFT"				: ["kLFT5", f"Ctrl+{ARROW_LEFT}", "Move the active window left"],
		"MOVE_WINDOW_RIGHT"				: ["kRIT5", f"Ctrl+{ARROW_RIGHT}", "Move the active window right"],
		"MOVE_WINDOW_UP"				: ["kUP5", f"Ctrl+{ARROW_UP}", "Move the active window up"],
		"MOVE_WINDOW_DOWN"				: ["kDN5", f"Ctrl+{ARROW_DOWN}", "Move the active window down"],
		"MOVE_CURSOR_LEFT"				: ["KEY_LEFT", ARROW_LEFT, "Move cursor left one character"],
		"MOVE_CURSOR_RIGHT"				: ["KEY_RIGHT", ARROW_RIGHT, "Move cursor right one character"],
		"MOVE_CURSOR_UP"				: ["KEY_UP", ARROW_UP, "Move cursor up one line"],
		"MOVE_CURSOR_DOWN"				: ["KEY_DOWN", ARROW_DOWN, "Move cursor down one line"],
		"DELETE_CHARACTER_RIGHT"		: ["KEY_DC", "Del", "Delete the character to the right of the cursor"],
		"DELETE_CHARACTER_LEFT"			: ["KEY_BACKSPACE", "Backspace", "Delete the character to the left of the cursor"],
		"SHOW_ACTIVE_TABS"				: ["^T", "Ctrl+T", "Showt the list of active tabs"],
		"SHOW_PROJECT_EXPLORER"			: ["^E", "Ctrl+E", "Open Project Explorer"],
		"SHOW_PREFERENCES"				: ["^P", "Ctrl+P", "Open the Preferences window"],
		"SHOW_HELP"						: [fn(1), "F1", "Show help"],
		"SHOW_RECENT_FILES"				: [fn(2), "F2", "Show the list of recent files"],
		"SWITCH_TO_PREVIOUS_EDITOR"		: [fn(3), "F3", "Switch to the previous editor in the active tab"],
		"SWITCH_TO_NEXT_EDITOR"			: [fn(4), "F4", "Switch to the next editor in the active tab"],
		"SWITCH_TO_PREVIOUS_TAB"		: [fn(5), "F5", "Switch to the previous tab"],
		"SWITCH_TO_NEXT_TAB"			: [fn(6), "F6", "Switch to the next tab"],
		"RESIZE_WINDOW"					: [ [fn(11), "KEY_RESIZE"], "F11", "Toggle fullscreen"],
		"TOGGLE_FILENAMES_IN_EDITORS"	: [ctrlfn(1), "Ctrl+F1", "Toggle display of filenames in non-active editors"],
		"CREATE_NEW_TAB"				: [ctrlfn(2), "Ctrl+F2", "Create a new tab"],
		"SPLIT_HORIZONTALLY"			: [ctrlfn(3), "Ctrl+F3", "Split horizontally"],
		"SPLIT_VERTICALLY"				: [ctrlfn(4), "Ctrl+F4", "Split vertically"],
		"MERGE_HORIZONTALLY"			: [ctrlfn(5), "Ctrl+F5", "Merge horizontally"],
		"MERGE_VERTICALLY"				: [ctrlfn(6), "Ctrl+F6", "Merge vertically"],
		"CLOSE_ACTIVE_TAB"				: [ctrlfn(7), "Ctrl+F7", "Close the active tab"],
		"CLOSE_ALL_EXCEPT_ACTIVE_EDITOR": [ctrlfn(9), "Ctrl+F9", "Close all but the active editor in the active tab"],
		"SHOW_COMMAND_WINDOW"			: ["^[", "Ctrl+[", "Open the command window"],
		
		"REFRESH_DIRECTORY_TREE"		: ["^R", "Ctrl+R", "Refresh the directory tree"],
		"CREATE_NEW_DIRECTORY"			: ["^D", "Ctrl+D", "Create a new directory under the selected directory"],
		"CREATE_NEW_FILE"				: ["^N", "Ctrl+N", "Create a new file under the selected directory"],
		"EXPAND_DIRECTORY"				: ["-", "- (minus)", "Expand the selected directory"],
		"COLLAPSE_DIRECTORY"			: ["+", "+ (plus)", "Collapse the selected directory"],
		"DELETE_FILE"					: ["KEY_DC", "Del", "Delete the selected file/directory"],
		"RENAME_FILE"					: [fn(2), "F2", "Rename the selected file/directory"],

		"CLOSE_EDITOR"					: ["^Q", "Ctrl+Q", "Close the active editor"],
		"SAVE"							: ["^S", "Ctrl+S", "Save the active buffer/file"],
		"SAVE_AS"						: [fn(9), "F9", "Save the active buffer/file with a new name"],
		"SAVE_AND_CLOSE_EDITOR"			: ["^W", "Ctrl+W", "Save and close the active editor"],
		"CUT"							: ["^X", "Ctrl+X", "Cut"],
		"COPY"							: ["^C", "Ctrl+C", "Copy"],
		"PASTE"							: ["^V", "Ctrl+V", "Paste"],
		"SELECT_ALL"					: ["^A", "Ctrl+A", "Select all"],
		"UNDO"							: ["^Z", "Ctrl+Z", "Undo"],
		"REDO"							: ["^Y", "Ctrl+Y", "Redo"],
		"GOTO_LINE"						: ["^G", "Ctrl+G", "Go to a specific line in the current document"],
		"SHOW_FIND"						: ["^F", "Ctrl+F", "Show the Find dialog-box"],
		"SHOW_FIND_AND_REPLACE"			: ["^H", "Ctrl+H", "Show the Find & Replace dialog-box"],
		"DECODE_UNICODE"				: [ctrlfn(2), "Ctrl+F2", "Decodes Unicode escape sequences (\\uxxxx) to characters"],
		"INSERT_TAB"					: ["^I", "Tab/Ctrl+I", "Insert tab/Increase selection indent"],
		"DECREASE_INDENT"				: ["KEY_BTAB", "Shift+Tab", "Decrease selection indent"],
		"NEWLINE"						: [["^J", "KEY_ENTER"], "Enter/Ctrl+J", "New line"],

		"FIND_NEXT"						: [[ "^J", "KEY_ENTER" ], "Enter/Ctrl+J", "Find the next match"],
		"FIND_PREVIOUS"					: [fn(7), "F7", "Find the previous match"],
		"REPLACE_NEXT"					: [fn(8), "F8", "Replace the current match (if any)"],
		"REPLACE_ALL"					: [ctrlfn(8), "Ctrl+F8", "Replace all occurrences"],

		"MOVE_CURSOR_TO_LINE_START"		: ["KEY_HOME", "Home", "Move to the beginning of the current line"],
		"MOVE_CURSOR_TO_LINE_END"		: ["KEY_END", "End", "Move the end of the current line"],
		"MOVE_CURSOR_TO_DOCUMENT_START" : ["kHOM5", "Ctrl+Home", "Move to the start of the current document"],
		"MOVE_CURSOR_TO_DOCUMENT_END"	: ["kEND5", "Ctrl+End", "Move to the end of the current document"],
		"MOVE_TO_PREVIOUS_PAGE"			: ["KEY_PPAGE", "PgUp", "Move to the previous page"],
		"MOVE_TO_NEXT_PAGE"				: ["KEY_NPAGE", "PgDown", "Move to the next page"],
		"SELECT_CHARACTER_RIGHT"		: ["KEY_SRIGHT", f"Shift+{ARROW_RIGHT}", "Select the character to the right"],
		"SELECT_CHARACTER_LEFT"			: ["KEY_SLEFT", f"Shift+{ARROW_LEFT}", "Select the character to the left"],
		"SELECT_LINE_ABOVE"				: ["KEY_SR", f"Shift+{ARROW_UP}", "Select the line above"],
		"SELECT_LINE_BELOW"				: ["KEY_SF", f"Shift+{ARROW_DOWN}", "Select the line below"],
		"SELECT_TILL_LINE_START"		: ["KEY_SHOME", "Shift+Home", "Select up to the start of the current line"],
		"SELECT_TILL_LINE_END"			: ["KEY_SEND", "Shift+End", "Select up to the end of the current line"],
		"MOVE_CURSOR_TO_NEXT_WORD"		: ["kRIT5", f"Ctrl+{ARROW_RIGHT}", "Move cursor right one word"],
		"MOVE_CURSOR_TO_PREVIOUS_WORD"	: ["kLFT5", f"Ctrl+{ARROW_LEFT}", "Move cursor left one word"],
		"SELECT_PAGE_ABOVE"				: ["KEY_SPREVIOUS", "Shift+PgUp", "Select the page above"],
		"SELECT_PAGE_BELOW"				: ["KEY_SNEXT", "Shift+PgDown", "Select the page below"],

		"SHOW_PROJECT_FIND"				: [fn(12), "F12", "Shows the find window for searching in all active buffers"],
		"SHOW_PROJECT_FIND_AND_REPLACE" : [ctrlfn(12), "Ctrl+F12", "Shows the find & replace window for all active buffers"],

		"RIGHT_CLICK"					: ["kRIT3", f"Alt+{ARROW_RIGHT}", "Right-click"],
		"HIDE_MENU_BAR"					: ["kUP3", f"Alt+{ARROW_UP}", "Hide menu bar"],
		"SHOW_MENU_BAR"					: ["kDN3", f"Alt+{ARROW_DOWN}", "Show menu bar"]
	}

	@classmethod
	def get_list_of_bindings(cls):
		blist = list()
		for command, key in cls.BINDINGS.items():
			blist.append( (key[1], key[2]) )
		return blist

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
	def write_key_bindings_to_file(cls):
		keyFile = open(KEY_BINDINGS_FILE, "wt")
		for command, key in cls.BINDINGS.items():
			if(type(key[0]) == str):
				keyFile.write("KEY_" + command + "=(" + key[0] + ";" + key[1] + ")\n")
			elif(type(key[0]) == list):
				x = "KEY_" + command + "=([" + key[0][0]
				for i in range(1, len(key[0])):
					x += "," + key[0][i]
				x += "];" + key[1] + ")\n"
				keyFile.write(x)
		keyFile.close()

	@classmethod
	def load_key_bindings_from_file(cls):
		if(not os.path.isfile(KEY_BINDINGS_FILE)): return
		keyFile = open(KEY_BINDINGS_FILE, "rt")
		data = keyFile.read().splitlines()
		keyFile.close()
		for d in data:
			if(not (d.startswith("KEY_") and d.find("=(") > -1 and d.endswith(")"))): continue
			temp = d[4:].strip().split("=(")
			command = temp[0].strip().upper()
			key = temp[1][:-1]
			temp = key.split(";")
			pretty = temp[1].strip()
			key = temp[0]
			
			if(key.startswith("[") and key.endswith("]")):
				key = key[1:-1].split(",")
				key_list = list()
				for k in key:
					key_list.append(k)
			else:
				key_list = key
				
			cls.BINDINGS[command][0] = key_list
			cls.BINDINGS[command][1] = pretty

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