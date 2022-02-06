# ---------------------------------------------------------------------------------------------
#  Copyright (c) Akash Nag. All rights reserved.
#  Licensed under the MIT License. See LICENSE.md in the project root for license information.
# ---------------------------------------------------------------------------------------------

# This module handles all commands entered through the command-window

from ash import *
import codecs

from ash.core.logger import log

class CommandInterpreter:
	def __init__(self, app, mw):
		self.app = app
		self.mw = mw
		
		self.commands = {
			"qa!"	: (self.app.dialog_handler.invoke_forced_quit, "Discard all unsaved changes and quit application"),
			"wq"	: (self.mw.save_and_close_active_editor, "Save and close the active editor"),
			"w"		: (self.mw.save_active_editor, "Save active editor"),
			"qt"	: (self.mw.close_active_tab, "Close active tab"),
			"hsplit": (self.mw.split_horizontally, "Split horizontally"),
			"vsplit": (self.mw.split_vertically, "Split vertically"),
			"hmerge": (self.mw.split_horizontally, "Merge horizontally"),
			"vmerge": (self.mw.split_vertically, "Merge vertically"),
			"rdisk" : (self.mw.reload_active_buffer_from_disk, "Discard unsaved changes and reload the active buffer from disk"),
			"!>"	: (self.execute_shell_command_in_background, "Executes a shell command and open the output in a new buffer"),
			"!"		: (self.execute_shell_command_in_terminal, "Executes a shell command in a new console")
		}

		self.prefix_commands = {
			"open"	: (self.open_file, "Open file:[param1]"),
			"wc"	: (self.write_a_copy, "Write a copy to file:[param1]"),
			"hso"	: (self.hsplit_open, "Splits window horizontally and opens self / file:[param1]"),
			"vso"	: (self.vsplit_open, "Splits window vertically and opens self / file:[param1]"),
			"!>"	: (self.execute_shell_command_in_background, "Executes a shell command and open the output in a new buffer"),
			"!"		: (self.execute_shell_command_in_terminal, "Executes a shell command in a new console")
		}

	def get_command_list(self):
		return {**self.commands, **self.prefix_commands}

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
			if(pos < 0): pos = len(command)
			func_info = self.prefix_commands.get(command[0:pos])
			if(func_info == None): 
				self.app.show_error(f"Command not found:\n'{command}'")
			else:
				self.__parse_and_call(command, pos, func_info)
	
	def __parse_and_call(self, command, pos, func_info):
		if(pos == len(command)):
			param_list = None
		else:
			param_list = command[pos+1:].split(" ")
		func = func_info[0]
		func(param_list)

	# <------------------------------ list of command processors ------------------------------>

	# Syntax: (filenames are relative to project if PROJECT_MODE)
	# open filename1 filename2 ...
	def open_file(self, params):
		for filename in params:
			if(not filename.startswith("/") and self.app.app_mode == APP_MODE_PROJECT):
				filename = self.app.project_dir + "/" + filename
			self.mw.open_in_new_tab(filename)

	# Syntax: (filenames are relative to project if PROJECT_MODE)
	# wc filename
	def write_a_copy(self, params):
		aed = self.mw.get_active_editor()
		if(aed == None or len(params)==0): return
		for filename in params:
			if(not filename.startswith("/") and self.app.app_mode == APP_MODE_PROJECT):
				filename = self.app.project_dir + "/" + filename
			aed.buffer.write_a_copy(filename)			

	# Syntax: (filenames are relative to project if PROJECT_MODE)
	# hso filename
	def hsplit_open(self, params):
		aed = self.mw.get_active_editor()
		if(aed == None): return
		if(params != None and len(params) == 1):
			filename = params[0]
			if(not filename.startswith("/") and self.app.app_mode == APP_MODE_PROJECT):
				filename = self.app.project_dir + "/" + filename
		else:
			filename = None
		if(filename == None):
			bid = aed.buffer.id
		else:
			bid = self.app.buffers.get_buffer_by_filename(filename)
			if(bid == None):
				bid, buffer = self.app.buffers.create_new_buffer(filename)
		self.mw.split_horizontally(bid)
		
	# Syntax: (filenames are relative to project if PROJECT_MODE)
	# vso filename
	def vsplit_open(self, params):
		aed = self.mw.get_active_editor()
		if(aed == None): return
		if(params != None and len(params) == 1):
			filename = params[0]
			if(not filename.startswith("/") and self.app.app_mode == APP_MODE_PROJECT):
				filename = self.app.project_dir + "/" + filename
		else:
			filename = None
		if(filename == None):
			bid = aed.buffer.id
		else:
			bid = self.app.buffers.get_buffer_by_filename(filename)
			if(bid == None):
				bid, buffer = self.app.buffers.create_new_buffer(filename)
		self.mw.split_vertically(bid)

	# Syntax:
	# \!> shell command
	def execute_shell_command_in_background(self, params=None):
		try:
			output = subprocess.check_output(params)
			output = output.decode("utf-8")

			filename = TEMP_OUTPUT_FILE
			with open(filename, "wt") as f:
				f.write(output)
			
			sel_buffer = self.app.buffers.get_buffer_by_filename(filename)
			if(sel_buffer == None):
				_, sel_buffer = self.app.buffers.create_new_buffer(filename=filename, encoding=None, has_backup=False)
			else:
				sel_buffer.reload_from_disk()

			self.app.main_window.invoke_activate_editor(sel_buffer.id, sel_buffer, True)
		except Exception as error:
			self.app.show_error("An error occurred while executing the shell command:\n" + str(error))

	# Syntax:
	# \! shell command
	def execute_shell_command_in_terminal(self, params=None):
		try:
			command = " ".join(params)
			x = f'{DEFAULT_TERMINAL} -hold -e "{command}"'
			subprocess.Popen(x, shell=True)
		except Exception as error:
			self.app.show_error("An error occurred while executing the shell command:\n" + str(error))
