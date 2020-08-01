# ---------------------------------------------------------------------------------------------
#  Copyright (c) Akash Nag. All rights reserved.
#  Licensed under the MIT License. See LICENSE.md in the project root for license information.
# ---------------------------------------------------------------------------------------------

# This module handles installation of keymaps

import ash
from ash.formatting.colors import *
from urllib.request import urlopen

from ash.utils import *
from ash.utils.keyUtils import *

class KeyMappingsManager:
	def __init__(self, app):
		self.app = app
		self.init_keymap()

	def get_default_key_bindings(self):
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
			"LIST_ACTIVE_BUFFERS"			: ["^L", "Ctrl+L", "List active files/buffers"],
			"FINALIZE_CHOICE"				: [[ "^J", "KEY_ENTER" ], "Ctrl+J/Enter", "Finalize the present choice/value"],
			
			"LIST_MOVE_SELECTION_UP"		: ["KEY_UP", ARROW_UP, "Move selection up in a list"],
			"LIST_MOVE_SELECTION_DOWN"		: ["KEY_DOWN", ARROW_DOWN, "Move selection down in a list"],
			"LIST_MOVE_SELECTION_NEXT"		: ["KEY_RIGHT", ARROW_RIGHT, "Open the next menu"],
			"LIST_MOVE_SELECTION_PREVIOUS"	: ["KEY_LEFT", ARROW_LEFT, "Open the previous menu"],
			"LIST_MOVE_TO_PREVIOUS_PAGE"	: ["KEY_PPAGE", "PgUp", "Move selection up one page"],
			"LIST_MOVE_TO_NEXT_PAGE"		: ["KEY_NPAGE", "PgDown", "Move selection down one page"],
			"LIST_MAKE_SELECTION"			: [[ "^J", "KEY_ENTER" ], "Ctrl+J/Enter", "Select the currently selected item"],
			"LIST_DELETE_SELECTION"			: ["KEY_DC", "Del", "Deletes the currently selected item"],
			"LIST_ADD_NEW"					: ["^N", "Ctrl+N", "Add a new item to the list"],
			
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
			"SHOW_ACTIVE_TABS"				: ["^T", "Ctrl+T", "Show the list of active tabs"],
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
			"SHOW_MENU_BAR"					: ["kDN3", f"Alt+{ARROW_DOWN}", "Show menu bar"],
			"SHOW_THEME_MANAGER"			: ["", f"<Unassigned>", "Show the theme manager window"],
			"SHOW_KEY_MAPPINGS_MANAGER"		: ["", f"<Unassigned>", "Show the key-mappings manager window"],
			"SHOW_ABOUT"					: ["", f"<Unassigned>", "Show the About... window"]
		}
		return BINDINGS

	def init_keymap(self):
		# write out the default keymap file (will reset any changes made to it)
		BINDINGS = self.get_default_key_bindings()
		self.write_out_keymap_file( os.path.join(ash.APP_KEYMAPS_DIR, "default.keymap"), BINDINGS )

		# load the current keymap from installed_keymaps
		installed_keymaps = self.get_installed_keymaps()
		sel_keymap = None
		sel_index = -1
		for i,t in enumerate(installed_keymaps):
			if(t[1] == True): 
				sel_keymap = t[0]
				sel_index = i
				break
		
		# if not default keymap, load keymap from file
		if(sel_index > 0):
			if(sel_keymap == None): sel_keymap = "default"
			sel_keymap_file = os.path.join(ash.APP_KEYMAPS_DIR, sel_keymap + ".keymap")
			if(not os.path.isfile(sel_keymap_file)):
				installed_keymaps.pop(sel_index)
				installed_keymaps.pop(0)
				installed_keymaps.insert( ("default", True))
				self.write_out_installed_keymaps(installed_keymaps)
			else:
				BINDINGS = load_keymap_from_file(sel_keymap_file)
		
		# set the current bindings
		KeyBindings.BINDINGS = BINDINGS

	def load_keymap_from_file(self, keymap_file):
		if(not os.path.isfile(keymap_file)): return

		BINDINGS = self.get_default_key_bindings()
		keyFile = open(keymap_file, "rt")
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
			
			BINDINGS[command][0] = key_list
			BINDINGS[command][1] = pretty
		
		return BINDINGS

	def get_installed_keymaps(self):
		if(not os.path.isfile(ash.INSTALLED_KEYMAPS_FILE)):
			installed_keymaps = [("default", True)]
			return installed_keymaps

		fp = open(ash.INSTALLED_KEYMAPS_FILE, "rt")
		keymap_names = fp.read().splitlines()
		fp.close()

		installed_keymaps = list()
		is_set = False
		for i, t in enumerate(keymap_names):
			x = t.strip().lower().split(",")
			if(i > 0 and x[0].strip() == "default"): continue
			installed_keymaps.append( ( x[0].strip(), bool(x[1].strip()) ) )			
			if(bool(x[1].strip()) == True): is_set = True
		
		if(len(installed_keymaps) == 0 or installed_keymaps[0][0] != "default"):
			installed_keymaps.insert(0, ("default", not is_set))

		return installed_keymaps

	def install_keymap(self, keymap_file):
		if(not keymap_file.endswith(".keymap")):
			self.app.show_error("Keymap files must end with .keymap")
			return

		if((not keymap_file.startswith("file://")) and (not keymap_file.startswith("http://")) and (not keymap_file.startswith("https://"))):
			self.app.show_error("Invalid URL protocol: use file:// for local files,\nhttp:// or https:// for remote files")
			return

		try:
			with urlopen(url=keymap_file) as f:
				keymap_data = f.read().decode("utf-8")
		except:
			self.app.show_error("An error occurred while fetching keymap")
			return
		
		if(get_file_title(keymap_file) == "default.keymap"):
			self.app.show_error("Cannot have keymap named 'default.keymap'")
			return

		local_keymap_file = os.path.join(ash.APP_KEYMAPS_DIR, get_file_title(keymap_file))
		if(os.path.isfile(local_keymap_file)):
			if(not self.app.ask_question("REPLACE KEYMAP", f"The keymap {get_file_title(keymap_file)} already exists, replace it?")): return

		fp = open(local_keymap_file, "wt")
		fp.write(keymap_data)
		fp.close()

		keymap_name = keymap_file[:-7]
		installed_keymaps = self.get_installed_keymaps()
		installed_keymaps.append( (keymap_name, False) )
		self.write_out_installed_keymaps(installed_keymaps)

	def set_keymap(self, keymap_name):
		sel_keymap_file = os.path.join(ash.APP_KEYMAPS_DIR, keymap_name + ".keymap")
		if(not os.path.isfile( sel_keymap_file )):
			self.app.show_error(f"Cannot find file: '{keymap_name}.keymap'")
			return
		
		BINDINGS = self.load_keymap_from_file(sel_keymap_file)
		KeyBindings.BINDINGS = BINDINGS

	def write_out_installed_keymaps(self, installed_keymaps):
		fp = open(ash.INSTALLED_KEYMAPS_FILE, "wt")
		for i in installed_keymaps:
			fp.write(f"{i[0]},{i[1]}\n")
		fp.close()

	def write_out_keymap_file(self, keymap_file, BINDINGS):
		keyFile = open(keymap_file, "wt")
		for command, key in BINDINGS.items():
			if(type(key[0]) == str):
				keyFile.write("KEY_" + command + "=(" + key[0] + ";" + key[1] + ")\n")
			elif(type(key[0]) == list):
				x = "KEY_" + command + "=([" + key[0][0]
				for i in range(1, len(key[0])):
					x += "," + key[0][i]
				x += "];" + key[1] + ")\n"
				keyFile.write(x)
		keyFile.close()

	def remove_installed_keymap(self, keymap_name):
		if(keymap_name == "default"):
			self.app.show_error("Cannot remove default keymap")
			return

		installed_keymaps = self.get_installed_keymaps()
		for i, t in enumerate(installed_keymaps):
			if(t[0] == keymap_name):
				installed_keymaps.pop(i)
				break

		self.write_out_installed_keymaps(installed_keymaps)