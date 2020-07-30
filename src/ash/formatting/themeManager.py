# ---------------------------------------------------------------------------------------------
#  Copyright (c) Akash Nag. All rights reserved.
#  Licensed under the MIT License. See LICENSE.md in the project root for license information.
# ---------------------------------------------------------------------------------------------

# This module handles installation of themes

import ash
from ash.formatting.colors import *
from urllib.request import urlopen

class ThemeManager:
	def __init__(self, app):
		self.app = app
		self.init_colors()

	def init_colors(self):
		# write out the default theme file (will reset any changes made to it)
		colors, element_colors = get_default_colors()
		self.write_out_theme_file( os.path.join(ash.APP_DATA_DIR, "default.theme"), colors, element_colors )

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
			sel_theme_file = os.path.join(ash.APP_DATA_DIR, sel_theme + ".theme")
			if(not os.path.isfile(sel_theme_file)):
				installed_themes.pop(sel_index)
				installed_themes.pop(0)
				installed_themes.insert( ("default", True))
				self.write_out_installed_themes(installed_themes, colors, element_colors)
			else:
				colors, element_colors = load_theme_from_file(sel_theme_file)
		
		# set the current theme
		set_colors(colors, element_colors)

	def load_theme_from_file(self, theme_file, colors = None, element_colors = None):
		if(colors == None): colors = dict()
		if(element_colors == None): element_colors = dict()

		configFile = open(theme_file, "rt")
		config = configFile.read().splitlines()
		configFile.close()

		for line in config:
			# syntax: 'magenta=rgb(113,154,132)'
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
		if(not theme_file.endswith(".theme")):
			self.app.show_error("Theme files must end with .theme")
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
		
		if(get_file_title(theme_file) == "default.theme"):
			self.app.show_error("Cannot have theme named 'default.theme'")
			return

		local_theme_file = os.path.join(ash.APP_DATA_DIR, get_file_title(theme_file))
		if(os.path.isfile(local_theme_file)):
			if(not self.app.ask_question("REPLACE THEME", f"The theme {get_file_title(theme_file)} already exists, replace it?")): return

		fp = open(local_theme_file, "wt")
		fp.write(theme_data)
		fp.close()

		theme_name = theme_file[:-6]
		installed_themes = get_installed_themes()
		installed_themes.append( (theme_name, False) )
		self.write_out_installed_themes(installed_themes)

	def set_theme(self, theme_name):
		sel_theme_file = os.path.join(ash.APP_DATA_DIR, sel_theme + ".theme")
		if(not os.path.isfile( sel_theme_file )):
			self.app.show_error(f"Cannot find file: '{theme_name}.theme'")
			return
		colors, element_colors = load_theme_from_file(sel_theme_file)
		set_colors(colors, element_colors)

	def write_out_installed_themes(self, installed_themes):
		fp = open(ash.INSTALLED_THEMES_FILE, "wt")
		for i in installed_themes:
			fp.write(f"{i[0]},{i[1]}\n")
		fp.close()

	def write_out_theme_file(self, theme_file, colors, element_colors):
		fp = open(theme_file, "wt")
		for name, rgb in colors.items():
			fp.write("color-" + name + " = rgb(" + str(int(rgb[0] // MULTIPLIER)) + ", " + str(int(rgb[1] // MULTIPLIER)) + ", " + str(int(rgb[2] // MULTIPLIER)) + ")\n")
		for name, pair in element_colors.items():
			fp.write("color-" + name + " = (" + pair[0] + ", " + pair[1] + ")\n")
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