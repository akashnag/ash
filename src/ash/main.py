# ---------------------------------------------------------------------------------------------
#  Copyright (c) Akash Nag. All rights reserved.
#  Licensed under the MIT License. See LICENSE.md in the project root for license information.
# ---------------------------------------------------------------------------------------------

import glob
from ash import *
from ash.dialogHandler import *

APP_VERSION			= "v1.0"

APP_MODE_FILE		= 1		# if ash is invoked with zero or more file names
APP_MODE_PROJECT	= 2		# if ash is invoked with a single directory name

class AshEditorApp:
	def __init__(self, args):
		self.args = args
		self.argc = len(args)
		self.dialog_handler = DialogHandler(self)
				
	def run(self):
		self.files = list()
		if(self.argc == 1):
			self.app_mode = APP_MODE_FILE
			self.files.append(FileData())
		elif(self.argc == 2 and os.path.isdir(self.args[1])):
			self.app_mode = APP_MODE_PROJECT			
			self.project_dir = str(pathlib.Path(self.args[1]).absolute())
			all_files = glob.glob(self.project_dir + "/**/*.*", recursive=True)
			for f in all_files:
				if(f.find("/__pycache__/") == -1): self.files.append(FileData(f))
		else:
			self.app_mode = APP_MODE_FILE
			for i in range(1, len(self.args)):
				if(os.path.isdir(self.args[i])):
					print("ERROR: cannot open more than 1 project")
					return
				filePath = str(pathlib.Path(self.args[i]).absolute())
				self.files.append(FileData(filePath))
		
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
		
		self.main_window = TopLevelWindow(self, self.stdscr, app_title, self.main_key_handler)
		self.main_window.add_status_bar(StatusBar(self.main_window, [ 10, 15, 28, 11, 23 ]))
		
		if(self.app_mode != APP_MODE_PROJECT):
			editor = Editor(self.main_window)
			editor.set_data(self.files[0])
			self.main_window.add_editor(editor)
			self.main_window.layout_manager.readjust(True)
		
		self.main_window.show()		
		
	# primary key handler to receive all key combinations from TopLevelWindow
	def main_key_handler(self, ch):
		#y, x = get_center_coords(self, 5, 40)
		#self.msgBox = MessageBox(self.stdscr, y, x, 5, 40, "INFO", "You pressed: " + str(curses.keyname(ch)) + "\n(O)K")
		#while(True):
		#	response = self.msgBox.show()
		#	if(response == MSGBOX_OK): break	
		#	beep()
		
		if(is_ctrl(ch, "Q")): 
			# for diagnostic purposes (since Ctrl+C is disabled)
			self.main_window.hide()
		elif(is_ctrl(ch, "L")):
			# adjust layout
			self.dialog_handler.invoke_switch_layout()
		elif(is_ctrl(ch, "O")):
			# open file
			aed = self.main_window.active_editor_index
			if(aed < 0):
				return self.show_error("No editor selected")
			elif(self.main_window.editors[aed].save_status == False):
				if(self.main_window.editors[aed].has_been_allotted_file or len(str(self.main_window.editors[aed])) > 0):
					return self.show_error("Current file must be saved first")
			
			if(self.app_mode == APP_MODE_PROJECT):
				self.dialog_handler.invoke_project_file_open()
			else:
				self.dialog_handler.invoke_file_open()
		elif(is_func(ch)):
			pass
			# focus on editor
			#aed = self.main_window.active_editor_index
			#ned = get_func_key(ch) - 1
			#if(ned == aed): return -1
			#self.main_window.active_editor_index = ned
			#if(not self.main_window.layout_manager.editor_exists(ned)):
			#	if(self.app_mode == APP_MODE_BLANK):
			#		self.main_window.editors[ned] = Editor(self.main_window)
			#	elif(self.app_mode == APP_MODE_FILE):
			#		fi = self.files[0] if ned >= len(self.files) else self.files[ned]
			#		self.main_window.editors[ned] = Editor(self.main_window)
			#		self.main_window.editors[ned].allot_and_open_file(fi)
			#	else:
			#		self.main_window.editors[ned] = Editor(self.main_window)
			#		self.dialog_handler.invoke_project_file_open()

			#self.main_window.editors[aed].blur()
			#self.main_window.editors[ned].focus()

		return ch

	def show_error(self, msg):
		y, x = get_center_coords(self, 5, len(msg)+4)
		self.msgBox = MessageBox(self.stdscr, y, x, 5, len(msg)+4, "ERROR", msg + "\n(O)K")
		while(True):
			response = self.msgBox.show()
			if(response == MSGBOX_OK): return -1
			beep()

	# <------------------------------ Dialog stubs ------------------------------------->

	# called from editor because filename is required
	def invoke_file_save_as(self, filename=None):
		self.dialog_handler.invoke_file_save_as(filename)

	# -----------------------------------------------------------------------------------

