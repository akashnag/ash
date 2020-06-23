# ---------------------------------------------------------------------------------------------
#  Copyright (c) Akash Nag. All rights reserved.
#  Licensed under the MIT License. See LICENSE.md in the project root for license information.
# ---------------------------------------------------------------------------------------------

import glob
from ash import *
from ash.dialogHandler import *

APP_VERSION			= "v1.0"
UNSAVED_BULLET		= "\u2022 "

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
		return (self.screen_height, self.screen_width)

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
		
		app_title = ("" if active_editor.save_status else UNSAVED_BULLET) + app_title
		return app_title

	# initialize the GUI
	def app_main(self, stdscr):
		self.stdscr = stdscr
		self.readjust()
		
		init_colors()
		curses.raw()
		
		self.main_window = TopLevelWindow(self, self.stdscr, "Ash " + APP_VERSION, self.main_key_handler)
		self.main_window.add_status_bar(StatusBar(self.main_window, [ 10, 20, 28, 11, -1 ]))
		
		if(self.app_mode != APP_MODE_PROJECT):
			editor = Editor(self.main_window)
			if(len(self.files) == 0):
				editor.set_data(FileData())
			else:
				editor.set_data(self.files[0])
			self.main_window.add_editor(editor)
			self.main_window.layout_manager.readjust(True)
		
		self.main_window.show()		# this call returns when main_window() is closed
		self.__destroy()
	
	# called on app_exit
	def __destroy(self):
		pass

	# primary key handler to receive all key combinations from TopLevelWindow
	def main_key_handler(self, ch):
		#if(self.show_error("You pressed: " + str(curses.keyname(ch)))):
		#	self.main_window.repaint()
		#	return -1
		
		if(is_ctrl(ch, "@")): 
			# force quits the app without saving
			self.dialog_handler.invoke_forced_quit()
		elif(is_ctrl(ch, "Q")): 
			# quits the active editor or the app
			self.dialog_handler.invoke_quit()
		elif(is_ctrl(ch, "L")):
			# adjust layout
			self.dialog_handler.invoke_switch_layout()
		elif(is_func(ch)):
			# F1 - F6 to select an active editor
			fn = get_func_key(ch)
			ned = fn - 1
			
			if(ned >=0 and ned <= 5):
				self.main_window.layout_manager.invoke_activate_editor(ned)
			elif(fn == 7):
				pass
			elif(fn == 8):
				pass
			elif(fn == 9):
				pass
			elif(fn == 12):
				pass
				
			return -1

		return ch

	# displays an error message
	def show_error(self, msg, error=True):
		msg_lines, msg_len = get_message_dimensions(msg)
		y, x = get_center_coords(self, msg_lines + 4, msg_len + 4)		
		self.msgBox = MessageBox(self.stdscr, y, x, msg_lines + 4, msg_len + 4, ("ERROR" if error else "INFORMATION"), msg + "\n(O)K")
		while(True):
			response = self.msgBox.show()
			if(response == MSGBOX_OK): 
				self.main_window.repaint()
				return -1
			beep()

	# displays a question
	def ask_question(self, title, question, hasCancel=False):
		msg_lines, msg_len = get_message_dimensions(question)
		y, x = get_center_coords(self, msg_lines + 4, msg_len + 4)
		self.msgBox = MessageBox(self.stdscr, y, x, msg_lines + 4, msg_len + 4, title, question + "\n(Y)ES / (N)O" + (" / (C)ANCEL" if hasCancel else ""))
		while(True):
			response = self.msgBox.show()
			if(response == MSGBOX_YES): 
				self.main_window.repaint()
				return True
			elif(response == MSGBOX_NO): 
				self.main_window.repaint()
				return False
			elif(hasCancel and response == MSGBOX_CANCEL):
				self.main_window.repaint()
				return None
			beep()

	# checks if buffer is up-to-date with file on disk
	def is_file_already_loaded(self, filename):
		n = len(self.files)
		for i in range(n):
			if(self.files[i].filename == filename):
				if(not self.files[i].save_status):
					return True			# do not reload from disk as buffer is updated
				else:
					return False		# can reload from disk

		# assumes that file is already present in the list
		# if file not present in list, do NOT call this function as returned value can be misinterpreted
		return False

	# <------------------------------ Dialog stubs ------------------------------------->

	# called from editor because filename is required
	def invoke_file_save_as(self, filename=None):
		self.dialog_handler.invoke_file_save_as(filename)

	# -----------------------------------------------------------------------------------

