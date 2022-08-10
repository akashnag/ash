# ---------------------------------------------------------------------------------------------
#  Copyright (c) Akash Nag. All rights reserved.
#  Licensed under the MIT License. See LICENSE.md in the project root for license information.
# ---------------------------------------------------------------------------------------------

# This module handles all language settings for Ash

import ash
import os
import json
from ash.gui import *

class LocalisationManager:
	def __init__(self, app):
		self.app = app
		self.locale = self.app.settings_manager.get_setting("ui_language")
		self.text_items = dict()
		self.init_locale()

	def get_locale_file(self):
		return os.path.join(ash.APP_LOCALES_DIR, self.locale + ash.LOCALE_FILE_EXTENSION)

	def refresh_locale(self):
		self.locale = self.app.settings_manager.get_setting("ui_language")
		self.text_items = dict()
		self.init_locale()

	def translate(self, text):
		if(text == None):
			return None
		elif(text in self.text_items):
			return self.text_items[text]
		else:
			lines = text.split("\n")
			#t_lines = [ self.text_items[line] if(line in self.text_items) else line for line in lines ]
			
			t_lines = []
			for line in lines:
				if(line in self.text_items):
					t_lines.append(self.text_items[line])
				else:
					pos = line.find(": ")			# to take care of text like:   Version: 0.1.0  (where 0.1.0 is dynamic and independent of language)
					if(pos > -1 and pos < len(line) - 2):
						left_part = line[:pos]
						right_part = line[pos:]
						if(left_part in self.text_items):
							t_lines.append(self.text_items[left_part] + right_part)
						else:
							t_lines.append(line)
							log(f"Translation missing [{self.locale}] >> \"{left_part}\": \"{left_part}\",")
					else:
						t_lines.append(line)
						log(f"Translation missing [{self.locale}] >> \"{line}\": \"{line}\",")
			
			return "\n".join(t_lines)

	def init_locale(self):
		# if directory not present, create it		
		if(not os.path.isdir(ash.APP_LOCALES_DIR)):
			os.mkdir(ash.APP_LOCALES_DIR)

		# write out the default language locale file (will reset any changes made to it)
		def_lang = self.app.settings_manager.get_default_settings()["ui_language"]
		self.write_locale_file(os.path.join(ash.APP_LOCALES_DIR, def_lang + ash.LOCALE_FILE_EXTENSION), self.get_default_text_items())

		# if current locale file not present, switch locale to default locale (also update settings)
		if(not os.path.isfile(self.get_locale_file())):
			self.locale = def_lang
			self.app.settings_manager.add_to_setting("ui_language", self.locale, is_list = False)
		
		# if locale file is present, read it
		self.text_items = self.read_locale_file(self.get_locale_file())

	def read_locale_file(self, filename):
		sFile = open(filename, "rt")
		data = json.load(sFile)
		sFile.close()
		return data

	def write_locale_file(self, filename, data):
		sFile = open(filename, "wt")
		json_object = json.dumps(data, indent = 4)
		sFile.write(json_object + "\n")
		sFile.close()

	def get_default_text_items(self):
		return {
			# top menu bar items
			"File": "File",
			"Edit": "Edit",
			"Search": "Search",
			"View": "View",			
			"Build": "Build",			
			"Window": "Window",
			"Help": "Help",

			# 'File' drop-down menu items
			"New File...": "New File...",
			"Open File/Folder...": "Open File/Folder...",
			"Save": "Save",
			"Save As...": "Save As...",
			"Save & Close": "Save & Close",
			"Save all": "Save all",
			"Close all": "Close all",
			"Exit": "Exit",

			# 'Edit' drop-down menu items
			"Undo": "Undo",
			"Redo": "Redo",
			"Cut": "Cut",
			"Copy": "Copy",
			"Paste": "Paste",
			"Select all": "Select All",
			"Select line": "Select Line",
			"Find...": "Find...",
			"Find & Replace...": "Find & Replace...",
			"Find in all files...": "Find in all files...",
			"Find & Replace in all files...": "Find & Replace in all files...",
			"Insert snippet...": "Insert snippet...",

			# 'View' drop-down menu items
			"Go to line...": "Go to line...",
			"Command Palette...": "Command Palette...",
			"Preferences...": "Preferences...",
			"Open tabs...": "Open tabs...",
			"Active Buffers/Files...": "Active Buffers/Files...",
			"Recent files...": "Recent files...",
			"Project Explorer...": "Project Explorer...",
			TICK_MARK + " Status bar": TICK_MARK + " Status bar",
			"Status bar": "Status bar",

			# 'Tools' drop-down menu items
			"Project Settings": "Project Settings",
			"Global Settings": "Global Settings",

			# 'Run' drop-down menu items
			"Compile file": "Compile file",
			"Execute file": "Execute file",
			"Build project": "Build project",
			"Execute project": "Execute project",

			# 'Window' drop-down menu items
			"New tab": "New tab",
			"Close active tab": "Close active tab",
			"Close active editor": "Close active editor",
			"Close all but active editor": "Close all but active editor",
			"Split horizontally": "Split horizontally",
			"Split vertically": "Split vertically",
			"Merge horizontally": "Merge horizontally",
			"Merge vertically": "Merge vertically",
			"Switch to next editor": "Switch to next editor",
			"Switch to previous editor": "Switch to previous editor",
			"Switch to next tab": "Switch to next tab",
			"Switch to previous tab": "Switch to previous tab",

			# 'Help' drop-down menu items
			"Key Bindings...": "Key Bindings...",
			"About...": "About...",

			"GO TO LINE": "GO TO LINE",
			"Line.Col: ": "Line.Col: ",
			"Invalid line number specified": "Invalid line number specified",

			"SAVE/DISCARD ALL": "SAVE/DISCARD ALL",
			"One or more unsaved files exist, choose:": "One or more unsaved files exist, choose:",
			"Yes: save all filed-changes and quit (unguaranteed in case of errors)": "Yes: save all filed-changes and quit (unguaranteed in case of errors)",
			"No: discard all unsaved changes and quit": "No: discard all unsaved changes and quit",
			"Cancel: don't quit": "Cancel: don't quit",

			"No recent files on record": "No recent files on record",
			"RECENT FILES/PROJECTS": "RECENT FILES/PROJECTS",			
			"Search:": "Search:",
			"Recent Files:": "Recent Files:",
			"Recent Projects:": "Recent Projects:",

			"ABOUT": "ABOUT",
			"Ash text-editor": "Ash text-editor",
			"Version": "Version",
			"Released": "Released",
			"© Copyright 2020-2022, Akash Nag. All rights reserved.": "© Copyright 2020-2022, Akash Nag. All rights reserved.",
			"Licensed under the MIT License.": "Licensed under the MIT License.",
			"For more information, visit:": "For more information, visit:",
			"Website": "Website",
			"GitHub": "GitHub",

			"CREATE IN NEW TAB": "CREATE IN NEW TAB",
			"Create buffer in new tab?": "Create buffer in new tab?",

			"OPEN FILE/FOLDER": "OPEN FILE/FOLDER",
			"File/Folder:": "File/Folder:",
			"(Empty directory)": "(Empty directory)",
			"Encoding: ": "Encoding: ",

			"SAVE AS": "SAVE AS",
			"Filename:": "Filename:",
			"(Empty directory)": "(Empty directory)",

			"Find: ": "Find: ",
			"Match case": "Match case",
			"Whole words": "Whole words",
			"Regex": "Regex",
			"Replace with: ": "Replace with: ",

			"COMMAND": "COMMAND",
			"Enter command:": "Enter command:",

			"EDITOR PREFERENCES": "EDITOR PREFERENCES",
			"Tab Width:": "Tab Width:",
			"Encoding:": "Encoding:",
			"Show line numbers": "Show line numbers",
			"Word wrap": "Word wrap",
			"Hard wrap": "Hard wrap",
			"Syntax highlighting": "Syntax highlighting",
			"Complete matching pairs": "Complete matching pairs",
			"Show scrollbar": "Show scrollbar",
			"Show git diff": "Show git diff",

			"ACTIVE TABS": "ACTIVE TABS",
			" editors)": " editors)",

			"ACTIVE FILES/BUFFERS": "ACTIVE FILES/BUFFERS",
			"(No active files)": "(No active files)",

			"ERROR": "ERROR",

			"HELP": "HELP",
			"Search: ": "Search: ",

			"Tab": "Tab",

			"INSERT SNIPPET": "INSERT SNIPPET",
			"Snippet:": "Snippet:",
			"(No snippets found)": "(No snippets found)",
			"Snippet not found!": "Snippet not found!",

			"Ready": "Ready",
			"Loading...": "Loading...",
			"PROJECT EXPLORER": "PROJECT EXPLORER",
			"Cannot open binary file!": "Cannot open binary file!",

			"Close": "Close",
			"Reload from disk": "Reload from disk",

			"(No recent files)": "(No recent files)",
			"(No recent projects)": "(No recent projects)",
			"Compiler for this file-type not set!": "Compiler for this file-type not set!",
			"Build command not set for this project!": "Build command not set for this project!",
			"Execution command not set for this project!": "Execution command not set for this project!",
		}