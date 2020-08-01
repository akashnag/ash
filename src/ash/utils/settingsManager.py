# ---------------------------------------------------------------------------------------------
#  Copyright (c) Akash Nag. All rights reserved.
#  Licensed under the MIT License. See LICENSE.md in the project root for license information.
# ---------------------------------------------------------------------------------------------

# This module handles all global settings for Ash

import ash
import os
import pickle

class SettingsManager:
	def __init__(self, app):
		self.app = app
		self.settings = None
		self.init_settings()

	def get_default_settings(self):
		SETTINGS = {
			"IGNORED_DIRECTORIES" 		: [ ".git", "__pycache__" ],
			"IGNORED_FILE_EXTENSIONS"	: [ ".class", ".tmp" ]
		}
		return SETTINGS

	def init_settings(self):
		if(os.path.isfile(ash.SETTINGS_FILE)):
			self.load_settings()
		else:
			self.settings = self.get_default_settings()
			self.write_settings()
			ash.SETTINGS = self.settings

	def write_settings(self):
		fp = open(ash.SETTINGS_FILE, "wb")
		pickle.dump(self.settings, fp, pickle.HIGHEST_PROTOCOL)
		fp.close()

	def load_settings(self):
		fp = open(ash.SETTINGS_FILE, "rb")
		self.settings = pickle.load(fp)
		fp.close()
		ash.SETTINGS = self.settings

	def get_setting(self, setting_name):
		return self.settings.get(setting_name)

	def add_to_setting(self, setting_name, item_to_add, is_list = True):
		if(is_list):
			setting = self.settings.get(setting_name)
			if(setting == None):
				self.settings[setting_name] = [ item_to_add ]
			else:
				self.settings[setting_name].append(item_to_add)
		else:
			self.settings[setting_name] = item_to_add
		ash.SETTINGS = self.settings
		self.write_settings()

	def remove_from_setting(self, setting_name, item_to_remove, is_list = True):
		if(is_list):
			setting = self.settings.get(setting_name)
			if(setting == None):
				return
			else:
				self.settings[setting_name].remove(item_to_remove)
		else:
			self.settings[setting_name] = None
		ash.SETTINGS = self.settings
		self.write_settings()