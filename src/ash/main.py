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
		self.files = None
		if(self.argc == 1):
			self.app_mode = APP_MODE_BLANK
		elif(self.argc == 2 and os.path.isdir(self.args[1])):
			self.app_mode = APP_MODE_PROJECT			
			self.project_dir = str(pathlib.Path(self.args[1]).absolute())
			# add code to recursively add all files to self.files
		else:
			self.app_mode = APP_MODE_FILE
			self.files = list()
			for i in range(1, len(self.args)):
				if(os.path.isdir(self.args[i])):
					print("ERROR: cannot open more than 1 project")
					return
				self.files.append(str(pathlib.Path(self.args[i]).absolute()))
		
		# invoke the GUI initialization routine
		curses.wrapper(self.app_main)

	# recalculates screen dimensions
	def readjust(self):
		self.screen_height, self.screen_width = self.stdscr.getmaxyx()

	# returns the version of Ash
	def get_app_version(self):
		return APP_VERSION

	# returns the appropriate app title
	def get_app_title(self, active_editor = None):
		app_title = "Ash " + APP_VERSION

		if(active_editor == None):
			if(self.app_mode == APP_MODE_PROJECT):
				app_title = "[" + get_file_title(self.project_dir) + "] - " + app_title
				return app_title
			else:
				return app_title

		if(self.app_mode == APP_MODE_FILE):
			app_title = get_file_title(active_editor.filename) + " - " + app_title
		elif(self.app_mode == APP_MODE_PROJECT):
			app_title = "[" + get_file_title(self.project_dir) + "] - " + app_title
			app_title = get_file_title(active_editor.filename) + " - " + app_title
		else:
			app_title = "Untitled - " + app_title
		
		app_title = ("" if active_editor.save_status else "\u2022 ") + app_title
		return app_title

	# initialize the GUI
	def app_main(self, stdscr):
		self.stdscr = stdscr
		self.readjust()
		
		init_colors()
		curses.raw()
		
		app_title = "Ash " + APP_VERSION
		if(self.app_mode == APP_MODE_FILE):
			app_title = get_file_title(self.files[0]) + " - " + app_title
		elif(self.app_mode == APP_MODE_PROJECT):
			app_title = "[" + get_file_title(self.project_dir) + "] - " + app_title

		self.main_window = TopLevelWindow(self, self.stdscr, app_title, self.key_handler)
		self.main_window.add_status_bar(StatusBar(self.main_window, [ 10, 15, 28, 11, 23 ]))
		
		if(self.app_mode != APP_MODE_PROJECT):
			editor = Editor(self.main_window)
			if(self.files != None and len(self.files) > 0):
				editor.allot_and_open_file(self.files[0])
			self.main_window.add_editor(editor)
		
		self.main_window.show()		
		
	# FOR TESTING: primary key handler to receive all key combinations
	def key_handler(self, ch):
		if(is_ctrl(ch, "Q")): self.main_window.hide()
		return ch

	def invoke_file_save_as(self, filename=None):
		self.readjust()
		y, x = get_center_coords(self, 4, 40)
		self.dlgSaveAs = ModalDialog(self.stdscr, y, x, 4, 40, "SAVE AS", self.file_save_as_key_handler)
		if(filename == None): filename = str(os.getcwd()) + "/untitled.txt"
		txtFileName = TextField(self.dlgSaveAs, 2, 2, 36, filename)
		self.dlgSaveAs.add_widget("txtFileName", txtFileName)
		self.dlgSaveAs.show()

	def file_save_as_key_handler(self, ch):
		if(is_ctrl(ch, "Q")): 
			self.dlgSaveAs.hide()
		elif(is_newline(ch)):
			txtFileName = self.dlgSaveAs.get_widget("txtFileName")
			if(not os.path.isfile(str(txtFileName))):
				self.save_or_overwrite(str(txtFileName))
				return ch
			else:
				y, x = get_center_coords(self, 5, 40)
				self.msgBox = MessageBox(self.stdscr, y, x, 5, 40, "Replace File", "File already exists, replace?\n(Y)es / (N)o")
				while(True):
					response = self.msgBox.show()
					if(response == MSGBOX_YES):	
						self.save_or_overwrite(str(txtFileName))
						return ch
					elif(response == MSGBOX_NO):
						self.dlgSaveAs.hide()
						return ch
					else:
						beep()

		return ch

	def save_or_overwrite(self, filename):
		self.dlgSaveAs.hide()
		try:
			self.main_window.do_save_as(filename)
			if(self.app_mode == APP_MODE_BLANK): self.app_mode = APP_MODE_FILE
		except:			
			y, x = get_center_coords(self, 5, 40)
			self.msgBox = MessageBox(self.stdscr, y, x, 5, 40, "ERROR", "An error occurred while saving file\n(O)K")
			while(True):
				response = self.msgBox.show()
				if(response == MSGBOX_OK): return
				beep()