# ---------------------------------------------------------------------------------------------
#  Copyright (c) Akash Nag. All rights reserved.
#  Licensed under the MIT License. See LICENSE.md in the project root for license information.
# ---------------------------------------------------------------------------------------------

# This module handles all settings for Ash

import ash
import os
import shutil
import json

class SettingsManager:
	def __init__(self, app):
		self.app = app
		self.settings = None
		self.init_settings()

	def get_default_settings(self):
		settings = {
			"ignored_directories" 		: [ ".git", "__pycache__", ".vscode", ".ash-editor" ],
			"ignored_file_extensions"	: [ ".class", ".tmp" ],
			"default_encoding"			: "utf-8",
			"compile_file_command"		: {
												".c"	: "gcc %f -o %e.o",
												".cpp"	: "g++ %f -o %e.o",
												".java"	: "javac %f"
											},
			"build_project_command"		: "",
			"execute_project_command"	: "",
			"execute_file_command"		: {
												".c"	: "%e.o",
												".cpp"	: "%e.o",
												".java" : "java -classpath %d %e",
												".py"	: "python3 %f"
											},
			"tab_width"					: 4,
			"scrollbars"				: False,
			"line_numbers"				: True,
			"wrap_text"					: False,
			"hard_wrap"					: True,
			"syntax_highlighting"		: True,
			"auto_close_matching_pairs"	: False
		}
		return settings

	def get_setting(self, setting_name):
		x = ash.SETTINGS.get(setting_name)
		if(x == None): x = self.get_default_settings().get(setting_name)
		return x

	def get_current_settings_file(self):
		if(self.app.app_mode == ash.APP_MODE_PROJECT):
			project_settings_dir = os.path.join(self.app.project_dir, ash.PROJECT_SETTINGS_DIR_NAME)
			return os.path.join(project_settings_dir, ash.PROJECT_SETTINGS_FILE_NAME)			
		else:
			return ash.SETTINGS_FILE

	def reload_settings(self):
		self.init_settings()

	def init_settings(self):
		if(not os.path.isfile(ash.SETTINGS_FILE)):
			self.write_settings(ash.SETTINGS_FILE, self.get_default_settings())

		if(self.app.app_mode == ash.APP_MODE_PROJECT):
			project_settings_dir = os.path.join(self.app.project_dir, ash.PROJECT_SETTINGS_DIR_NAME)
			self.settings_file = os.path.join(project_settings_dir, ash.PROJECT_SETTINGS_FILE_NAME)
			if(not os.path.isdir(project_settings_dir)): os.mkdir(project_settings_dir)
			if(not os.path.isfile(self.settings_file)): shutil.copyfile(ash.SETTINGS_FILE, self.settings_file)
		else:
			self.settings_file = ash.SETTINGS_FILE

		ash.SETTINGS = self.load_settings(self.settings_file)

	def write_settings(self, filename, settings):
		sFile = open(filename, "wt")
		json_object = json.dumps(settings, indent = 4)
		sFile.write(json_object)
		sFile.close()

	def load_settings(self, filename):
		sFile = open(filename, "rt")
		settings = json.load(sFile)
		sFile.close()
		return settings

	def add_multi_setting(self, data):
		for key, value in data.items():
			ash.SETTINGS[key] = value
		self.write_settings(self.settings_file, ash.SETTINGS)

	def add_to_setting(self, setting_name, item_to_add, is_list = True):
		if(is_list):
			setting = ash.SETTINGS.get(setting_name)
			if(setting == None):
				ash.SETTINGS[setting_name] = [ item_to_add ]
			else:
				ash.SETTINGS[setting_name].append(item_to_add)
		else:
			ash.SETTINGS[setting_name] = item_to_add
		self.write_settings(self.settings_file, ash.SETTINGS)

	def remove_from_setting(self, setting_name, item_to_remove, is_list = True):
		if(is_list):
			setting = ash.SETTINGS.get(setting_name)
			if(setting == None):
				return
			else:
				ash.SETTINGS[setting_name].remove(item_to_remove)
		else:
			ash.SETTINGS[setting_name] = None
		self.write_settings(self.settings_file, ash.SETTINGS)