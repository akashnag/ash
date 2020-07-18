# ---------------------------------------------------------------------------------------------
#  Copyright (c) Akash Nag. All rights reserved.
#  Licensed under the MIT License. See LICENSE.md in the project root for license information.
# ---------------------------------------------------------------------------------------------

# This module handles all commands entered through the command-window

class CommandInterpreter:
	def __init__(self, app, mw):
		self.app = app
		self.mw = mw
		self.commands = {
			"hsplit": (self.mw.split_horizontally, "Split horizontally"),
			"vsplit": (self.mw.split_vertically, "Split vertically"),
			"hmerge": (self.mw.split_horizontally, "Merge horizontally"),
			"vmerge": (self.mw.split_vertically, "Merge vertically")
		}

	def get_command_list(self):
		return self.commands

	def interpret_command(self, command):
		if(command == None): return
		command = command.strip().lower()
		if(len(command) == 0): return
		func_info = self.commands.get(command)
		if(func_info != None):
			func = func_info[0]
			func()
		else:
			#TODO: check formatted commands (e.g. s/search/replace/gc)
			self.app.show_error(f"Command not found:\n'{command}'")