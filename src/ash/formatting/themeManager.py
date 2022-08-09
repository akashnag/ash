# ---------------------------------------------------------------------------------------------
#  Copyright (c) Akash Nag. All rights reserved.
#  Licensed under the MIT License. See LICENSE.md in the project root for license information.
# ---------------------------------------------------------------------------------------------

# This module handles installation of themes

import ash
import os
import json
from ash.formatting.colors import *

class ThemeManager:
	def __init__(self, app):
		self.app = app
		self.theme = self.app.settings_manager.get_setting("theme")
		self.init_colors()

	def get_theme_file(self):
		return os.path.join(ash.APP_THEMES_DIR, self.theme + ash.THEME_FILE_EXTENSION)

	def init_colors(self):
		# if directory not present, create it		
		if(not os.path.isdir(ash.APP_THEMES_DIR)):
			os.mkdir(ash.APP_THEMES_DIR)

		# write out the default theme file (will reset any changes made to it)
		def_theme = self.app.settings_manager.get_default_settings()["theme"]
		self.write_out_theme_file(os.path.join(ash.APP_THEMES_DIR, def_theme + ash.THEME_FILE_EXTENSION), *get_default_colors())

		# if current theme file not present, switch theme to default theme (also update settings)
		if(not os.path.isfile(self.get_theme_file())):
			self.theme = def_theme
			self.app.settings_manager.add_to_setting("theme", self.theme, is_list = False)
		
		# if theme file is present, read it
		colors, element_colors = self.load_theme_from_file(self.get_theme_file())

		# set the current theme
		if(not set_colors(colors, element_colors)):
			self.app.supports_colors = False

	def load_theme_from_file(self, theme_file, colors = None, element_colors = None):
		if(colors == None): colors = dict()
		if(element_colors == None): element_colors = dict()

		"""
			Theme file should be a JSON file
			it should contain two top-level keys: 'colors', and 'elements'
			each should have multiple key and value pairs
		
			Example syntax:

			{
				"colors": {
					"magenta" : "rgb(113,154,132)",
					"black": "rgb(0,0,0)"
					...
				},
				"elements": {
					"background": "(white,black)",
					...
				}
			}
		"""

		configFile = open(theme_file, "rt")
		config = json.load(configFile)
		configFile.close()

		temp_colors = config["colors"]
		temp_elements = config["elements"]

		for color_name, color_value in temp_colors.items():
			color_name = color_name.strip().lower()
			color_value = color_value.strip().lower()
			if(color_value.startswith("rgb(") and color_value.endswith(")")):
				triplet = color_value[4:-1].split(",")
				if(len(triplet) == 3):
					rgb = ( round(int(triplet[0]) * MULTIPLIER), round(int(triplet[1]) * MULTIPLIER), round(int(triplet[2]) * MULTIPLIER) )
					colors[color_name] = rgb

		for element_name, color_value in temp_elements.items():
			element_name = element_name.strip()
			color_value = color_value.strip().lower()
			if(color_value.startswith("(") and color_value.endswith(")")):
				pair = color_value[1:-1].split(",")
				if(len(pair) == 2):
					element_colors[element_name] = (pair[0].strip(), pair[1].strip())

		return (colors, element_colors)

	def refresh_theme(self):
		self.theme = self.app.settings_manager.get_setting("theme")
		self.init_colors()

	def write_out_theme_file(self, theme_file, colors, element_colors):
		data = {
			"colors": dict(),
			"elements": dict()
		}
		
		for color_name, rgb in colors.items():
			color_value = "rgb(" + str(int(rgb[0] // MULTIPLIER)) + ", " + str(int(rgb[1] // MULTIPLIER)) + ", " + str(int(rgb[2] // MULTIPLIER)) + ")"
			data["colors"][color_name] = color_value
		
		for element_name, color_pair in element_colors.items():
			data["elements"][element_name] = f"({color_pair[0]}, {color_pair[1]})"

		json_object = json.dumps(data, indent = 4)
		fp = open(theme_file, "wt")
		fp.write(json_object + "\n")
		fp.close()

