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
		return os.path.join(ash.APP_LOCALES_DIR, self.locale + ".json")

	def refresh_locale(self):
		self.locale = self.app.settings_manager.get_setting("ui_language")
		self.text_items = dict()
		self.init_locale()

	def translate(self, text):
		if(text in self.text_items):
			return self.text_items[text]
		else:
			return text			# return text unchanged in original language

	def init_locale(self):
		# if directory not present, create it		
		if(not os.path.isdir(ash.APP_LOCALES_DIR)):
			os.mkdir(ash.APP_LOCALES_DIR)

		# write out the default language locale file (will reset any changes made to it)
		def_lang = self.app.settings_manager.get_default_settings()["ui_language"]
		self.write_locale_file(os.path.join(ash.APP_LOCALES_DIR, def_lang + ".json"), self.get_default_text_items())

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
		# TODO: add code
		return {
			# top menu bar items
			"File": "File",
			"Edit": "Edit",
			"View": "View",
			"Tools": "Tools",
			"Run": "Run",
			"Window": "Window",
			"Help": "Help",

			# 'File' drop-down menu items
			"New File...": "New File...",
			"Open File/Project...": "Open File/Project...",
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
			"Key Bindings": "Key Bindings",
			"About...": "About..."

			"GO TO LINE": "GO TO LINE",
			"Line.Col: ": "Line.Col: ",
			"Invalid line number specified": "Invalid line number specified",

			"SAVE/DISCARD ALL": "SAVE/DISCARD ALL",
			"One or more unsaved files exist, choose:\nYes: save all filed-changes and quit (unguaranteed in case of errors)\nNo: discard all unsaved changes and quit\nCancel: don't quit": "One or more unsaved files exist, choose:\nYes: save all filed-changes and quit (unguaranteed in case of errors)\nNo: discard all unsaved changes and quit\nCancel: don't quit",
			
		}