# ---------------------------------------------------------------------------------------------
#  Copyright (c) Akash Nag. All rights reserved.
#  Licensed under the MIT License. See LICENSE.md in the project root for license information.
# ---------------------------------------------------------------------------------------------

from ash import *

APP_VERSION			= "v1.0"

APP_MODE_BLANK		= 1		# if ash is invoked without arguments
APP_MODE_FILE		= 2		# if ash is invoked with one or more file names
APP_MODE_PROJECT	= 3		# if ash is invoked with a single directory name

class AshEditorApp:
	def __init__(self, args):
		self.args = args
		self.argc = len(args)
				
	def run(self):
		# check arguments and set flags
		if(self.argc == 1):
			self.app_mode = APP_MODE_BLANK
			self.active_file1 = None
			self.active_file2 = None
		elif(self.argc == 2 and os.path.isdir(self.args[1])):
			self.app_mode = APP_MODE_PROJECT			
			self.project_dir = str(pathlib.Path(self.args[1]).absolute())
			self.active_file1 = None
			self.active_file2 = None
		else:
			self.app_mode = APP_MODE_FILE
			self.files = list()
			for i in range(1, len(self.args)):
				if(os.path.isdir(self.args[i])):
					print("ERROR: cannot open more than 1 project")
					return
				self.files.append(str(pathlib.Path(self.args[i]).absolute()))
		
			self.active_file1 = self.files[0]
			self.active_file2 = None

		# invoke the GUI initialization routine
		curses.wrapper(self.app_main)

	# initialize the GUI
	def app_main(self, stdscr):
		init_colors()
		curses.raw()
		
		app_title = "Ash " + APP_VERSION
		if(self.app_mode == APP_MODE_FILE):
			app_title = get_file_title(self.files[0]) + " - " + app_title
		elif(self.app_mode == APP_MODE_PROJECT):
			app_title = "[" + get_file_title(self.project_dir) + "] - " + app_title

		self.main_window = TopLevelWindow(stdscr, app_title, self.key_handler)
		self.main_window.add_status_bar(StatusBar(self.main_window, [ 10, 15, 28, 11, 23 ]))
		
		if(self.app_mode != APP_MODE_PROJECT):
			editor1 = Editor(self.main_window, 1, 0, 2, 0)
			if(self.active_file1 != None): 
				editor1.allot_and_open_file(self.active_file1)
			self.main_window.set_editors(editor1, None)
		
		self.main_window.show()
		
	# FOR TESTING: primary key handler to receive all key combinations
	def key_handler(self, ch):
		if(is_ctrl(ch, "Q")): self.main_window.hide()
		return ch