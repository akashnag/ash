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
			"q!"	: (self.app.dialog_handler.invoke_forced_quit, "Discard all unsaved changes and quit application"),
			"wq"	: (self.mw.save_and_close_active_editor, "Save and close the active editor"),
			"w"		: (self.mw.save_active_editor, "Save active editor"),
			"qt"	: (self.mw.close_active_tab, "Close active tab"),
			"hsplit": (self.mw.split_horizontally, "Split horizontally"),
			"vsplit": (self.mw.split_vertically, "Split vertically"),
			"hmerge": (self.mw.split_horizontally, "Merge horizontally"),
			"vmerge": (self.mw.split_vertically, "Merge vertically"),
			"rdisk" : (self.mw.reload_active_buffer_from_disk, "Discard unsaved changes and reload the active buffer from disk")
		}
		self.prefix_commands = {
			"o"		: (self.open_file, " ", "Open file specified by [param1]"),
			"wc"	: (self.write_a_copy, " ", "Write a copy of the active buffer to disk")
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
			pos = command.find(" ")
			func_info = (None if pos < 0 else self.prefix_commands.get(command[0:pos]))
			if(func_info == None): self.app.show_error(f"Command not found:\n'{command}'")
			self.__parse_and_call(command, pos, func_info)
	
	def __parse_and_call(self, command, pos, func_info):
		param_list = command[pos+1:].split(func_info[1])
		func = func_info[0]
		func(param_list)

	# <------------------------------ list of command processors ------------------------------>

	# Syntax: (filenames are relative to project if PROJECT_MODE)
	# o filename1 filename2 ...
	# o dirname
	def open_file(self, params):
		#TODO: load a file from disk (or buffer if it exists there)
		pass

	# Syntax: (filenames are relative to project if PROJECT_MODE)
	# wc filename
	def write_a_copy(self, params):
		#TODO: write out a copy of the current buffer to disk
		pass