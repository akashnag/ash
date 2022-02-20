# ---------------------------------------------------------------------------------------------
#  Copyright (c) Akash Nag. All rights reserved.
#  Licensed under the MIT License. See LICENSE.md in the project root for license information.
# ---------------------------------------------------------------------------------------------

# This module handles installation of themes

import ash
import json
from ash.formatting.colors import *
from urllib.request import urlopen

class ThemeManager:
	def __init__(self, app):
		self.app = app
		self.init_colors()

	def init_colors(self):
		# write out the default theme file (will reset any changes made to it)
		colors, element_colors = get_default_colors()
		self.write_out_theme_file( os.path.join(ash.APP_THEMES_DIR, "default.json"), colors, element_colors )

		# load the current theme from installed_themes
		installed_themes = self.get_installed_themes()
		sel_theme = None
		sel_index = -1
		for i,t in enumerate(installed_themes):
			if(t[1] == True): 
				sel_theme = t[0]
				sel_index = i
				break
		
		# if not default theme, load theme from file
		if(sel_index > 0):
			if(sel_theme == None): sel_theme = "default"
			sel_theme_file = os.path.join(ash.APP_THEMES_DIR, sel_theme + ".json")
			if(not os.path.isfile(sel_theme_file)):
				installed_themes.pop(sel_index)
				installed_themes.pop(0)
				installed_themes.insert( ("default", True))
				self.write_out_installed_themes(installed_themes, colors, element_colors)
			else:
				colors, element_colors = self.load_theme_from_file(sel_theme_file)
		
		# set the current theme
		if(not set_colors(colors, element_colors)):
			self.app.supports_colors = False

	def load_theme_from_file(self, theme_file, colors = None, element_colors = None):
		if(colors == None): colors = dict()
		if(element_colors == None): element_colors = dict()

		"""
			Theme file should be a JSON file (with extension .theme)
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
			element_name = element_name.strip().lower()
			color_value = color_value.strip().lower()
			if(color_value.startswith("(") and color_value.endswith(")")):
				pair = color_value[1:-1].split(",")
				if(len(pair) == 2):
					element_colors[element_name] = (pair[0].strip(), pair[1].strip())

		return (colors, element_colors)

	def get_installed_themes(self):
		if(not os.path.isfile(ash.INSTALLED_THEMES_FILE)):
			installed_themes = [("default", True)]
			return installed_themes

		fp = open(ash.INSTALLED_THEMES_FILE, "rt")
		theme_names = fp.read().splitlines()
		fp.close()

		installed_themes = list()
		is_set = False
		for i, t in enumerate(theme_names):
			x = t.strip().lower().split(",")
			if(i > 0 and x[0].strip() == "default"): continue
			installed_themes.append( ( x[0].strip(), bool(x[1].strip()) ) )			
			if(bool(x[1].strip()) == True): is_set = True
		
		if(len(installed_themes) == 0 or installed_themes[0][0] != "default"):
			installed_themes.insert(0, ("default", not is_set))

		return installed_themes

	def install_theme(self, theme_file):
		if(not theme_file.endswith(".json")):
			self.app.show_error("Theme files must end with .json")
			return

		if((not theme_file.startswith("file://")) and (not theme_file.startswith("http://")) and (not theme_file.startswith("https://"))):
			self.app.show_error("Invalid URL protocol: use file:// for local files,\nhttp:// or https:// for remote files")
			return

		try:
			with urlopen(url=theme_file) as f:
				theme_data = f.read().decode("utf-8")
		except:
			self.app.show_error("An error occurred while fetching theme")
			return
		
		if(get_file_title(theme_file) == "default.json"):
			self.app.show_error("Cannot have theme named 'default.json'")
			return

		local_theme_file = os.path.join(ash.APP_THEMES_DIR, get_file_title(theme_file))
		if(os.path.isfile(local_theme_file)):
			if(not self.app.ask_question("REPLACE THEME", f"The theme {get_file_title(theme_file)} already exists, replace it?")): return

		fp = open(local_theme_file, "wt")
		fp.write(theme_data)
		fp.close()

		theme_name = theme_file[:-6]
		installed_themes = self.get_installed_themes()
		installed_themes.append( (theme_name, False) )
		self.write_out_installed_themes(installed_themes)

	def set_theme(self, theme_name):
		sel_theme_file = os.path.join(ash.APP_THEMES_DIR, theme_name + ".json")
		if(not os.path.isfile( sel_theme_file )):
			self.app.show_error(f"Cannot find file: '{theme_name}.json'")
			return
		colors, element_colors = self.load_theme_from_file(sel_theme_file)
		if(not set_colors(colors, element_colors)):
			self.app.supports_colors = False

	def write_out_installed_themes(self, installed_themes):
		fp = open(ash.INSTALLED_THEMES_FILE, "wt")
		for i in installed_themes:
			fp.write(f"{i[0]},{i[1]}\n")
		fp.close()

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
		fp.write(json_object)
		fp.close()

	def remove_installed_theme(self, theme_name):
		if(theme_name == "default"):
			self.app.show_error("Cannot remove default theme")
			return

		installed_themes = self.get_installed_themes()
		for i, t in enumerate(installed_themes):
			if(t[0] == theme_name):
				installed_themes.pop(i)
				break
			
		self.write_out_installed_themes(installed_themes)