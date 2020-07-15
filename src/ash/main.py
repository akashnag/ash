# ---------------------------------------------------------------------------------------------
#  Copyright (c) Akash Nag. All rights reserved.
#  Licensed under the MIT License. See LICENSE.md in the project root for license information.
# ---------------------------------------------------------------------------------------------

# This is main app class

from ash import *

import time

from ash.core.bufferManager import *
from ash.core.logger import *

from ash.utils.utils import *
from ash.utils.keyUtils import *
from ash.utils.fileUtils import *

from ash.formatting.colors import *
from ash.formatting.formatting import *

from ash.gui.topLevelWindow import *
from ash.gui.editor import *
from ash.gui.statusbar import *
from ash.gui.msgBox import *
from ash.gui.inputBox import *
from ash.gui.dialogHandler import *

class AshEditorApp:
	def __init__(self, ash_dir, args):
		self.ash_dir = ash_dir
		self.args = args
		self.argc = len(args)
		self.dialog_handler = DialogHandler(self)
		log_init()
		recent_files_init()
		
	def load_files(self, progress_handler = None):
		self.buffers = BufferManager()
		
		if(self.argc == 1):
			self.app_mode = APP_MODE_FILE
		elif(self.argc == 2 and os.path.isdir(self.args[1])):
			self.app_mode = APP_MODE_PROJECT
			self.project_dir = str(os.path.abspath(self.args[1]))
			all_files = glob.glob(self.project_dir + "/**/*", recursive=True)

			for i, f in enumerate(all_files):
				if(not os.path.isfile(f)): continue
				if(should_ignore_file(f)): continue
				if(BufferManager.is_binary(f)): continue
				has_backup = BufferManager.backup_exists(f)
				self.buffers.create_new_buffer(filename=f, has_backup=has_backup)
				if(progress_handler != None): 
					progress = ( ( i / len(all_files) ) * 100 )
					progress_handler("Loading...", progress)
		else:
			self.app_mode = APP_MODE_FILE
			for i in range(1, len(self.args)):
				if(os.path.isdir(self.args[i])):
					print("ERROR: cannot open more than 1 project")
					return
				filePath = str(os.path.abspath(self.args[i]))
				if(BufferManager.is_binary(filePath)): continue
				has_backup = BufferManager.backup_exists(filePath)
				self.buffers.create_new_buffer(filename=filePath, has_backup=has_backup)
				if(progress_handler != None): 
					progress = ( ( i / (len(self.args)-1) ) * 100 )
					progress_handler("Loading...", progress)
		
		if(progress_handler != None): progress_handler("Ready", None)

	def run(self):		
		# invoke the GUI initialization routine
		ret_code = curses.wrapper(self.app_main)
		return ret_code

	# recalculates screen dimensions
	def readjust(self):
		self.screen_height, self.screen_width = self.stdscr.getmaxyx()
		return (self.screen_height, self.screen_width)

	# returns the version of Ash
	def get_app_version(self):
		return APP_VERSION

	# returns the name of the application
	def get_app_name(self):
		return "ash-" + APP_VERSION
	
	# initialize the GUI
	def app_main(self, stdscr):
		self.stdscr = stdscr
		self.readjust()
				
		init_colors()
		curses.raw()
		
		self.main_window = TopLevelWindow(self, self.stdscr, "ash " + APP_VERSION, self.main_key_handler)
		
		# status-bar sections: total=101+1 (min)
		# *status (8), *file-type (11), encoding(7), sloc (20), file-size (10), 
		# *unsaved-file-count (4), *tab-size (1), cursor-position (6+1+6+3+8=24)
		self.main_window.add_status_bar(StatusBar(self.main_window, [ 10, 13, 9, 22, 12, 6, 3, -1 ]))				
		self.readjust()
		self.main_window.layout_manager.readjust(True)		
		self.load_files(self.progress_handler)

		if(self.app_mode == APP_MODE_FILE):
			if(len(self.buffers) > 0):
				bid = 0
				buffer = self.buffers.get_buffer_by_id(bid)
				self.main_window.layout_manager.invoke_activate_editor(0, bid, buffer)
			elif(len(self.buffers) == 0):
				# comment the following 2 lines if you want to start ash with no buffers opened
				bid, buffer = self.buffers.create_new_buffer()
				self.main_window.layout_manager.invoke_activate_editor(0, bid, buffer)
		
		welcome_msg = f"ash-{APP_VERSION} | Ctrl+F1: Help"
		if(self.screen_width < MIN_WIDTH or self.screen_height < MIN_HEIGHT):
			welcome_msg = f"insufficient screen space, ash may crash unexpectedly; reqd.: {MIN_WIDTH}x{MIN_HEIGHT}"

		self.main_window.show(welcome_msg)		# this call returns when main_window() is closed		
		self.__destroy()
		
		return 0
	
	# shows progress in the status bar
	def progress_handler(self, msg, progress):
		if(progress == None):
			self.main_window.repaint(f"{msg}")
		else:
			progress_line = "\u2501" * int((progress/100) * (self.screen_width - 9 - len(msg)))
			self.main_window.repaint(f"{int(progress)}% {progress_line} {msg}")	

	# called on app_exit
	def __destroy(self):
		self.buffers.destroy()

	# primary key handler to receive all key combinations from TopLevelWindow
	def main_key_handler(self, ch):
		#if(self.show_error("You pressed: " + str(curses.keyname(ch)))):
		#	self.main_window.repaint()
		#	return -1
		
		# NOTE: whenever a key-combo is being handled here that may also be triggered
		# in an active editor (e.g. Ctrl+O), always:
		#	(i) add a check in the condition to ensure no active editors exist
		#	(ii) and, return -1 to prevent it being handled again if a new active editor
		#		 is created in the process of the handling

		if(is_ctrl(ch, "@")): 
			# force quits the app without saving
			self.dialog_handler.invoke_forced_quit()
			return -1
		elif(is_ctrl(ch, "Q")): 
			# quits the active editor or the app
			self.dialog_handler.invoke_quit()
			return -1
		elif(is_func(ch, 11) or ch == curses.KEY_RESIZE):
			self.readjust()
			self.main_window.repaint()
			return -1
		elif(is_ctrl(ch, "L")):
			# adjust layout
			self.dialog_handler.invoke_switch_layout()
			return -1
		elif(is_ctrl(ch, "E") and self.app_mode == APP_MODE_PROJECT):
			# project explorer
			self.dialog_handler.invoke_project_explorer()
			return -1
		elif(is_ctrl(ch, "N") and self.main_window.get_active_editor() == None):
			# file-new
			self.dialog_handler.invoke_file_new()
			return -1
		elif(is_ctrl(ch, "O") and self.main_window.get_active_editor() == None):
			# file-open
			self.dialog_handler.invoke_file_open()
			return -1		
		elif(is_func(ch)):
			# F1 - F6 to select an active editor
			# F7 - find previous
			# F8 - replace
			# Ctrl+F8 - replace all
			# Ctrl+F1 - help
			# F12 - recent files

			fn = get_func_key(ch)
			ned = fn - 1
			
			if(ned >=0 and ned <= 5):
				self.main_window.layout_manager.invoke_activate_editor(ned)
				return -1
			elif(is_ctrl_and_func(ch, 1)):
				self.dialog_handler.invoke_help_key_bindings()
				return -1
			elif(fn == 12):
				self.dialog_handler.invoke_recent_files()
				return -1

		return ch

	# displays an error message
	def show_error(self, msg, error=True):
		try:
			self.msgBox = MessageBox(self, ("ERROR" if error else "INFORMATION"), msg)
		except:
			self.warn_insufficient_screen_space()
			raise

		while(True):
			response = self.msgBox.show()
			if(response == MSGBOX_OK): 
				self.main_window.repaint()
				return -1
			beep()

	# displays a question
	def ask_question(self, title, question, hasCancel=False):
		try:
			self.msgBox = MessageBox(self, title, question, (MSGBOX_TYPE_YES_NO_CANCEL if hasCancel else MSGBOX_TYPE_YES_NO))
		except:
			self.warn_insufficient_screen_space()
			raise

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

	# displays an inputbox
	def prompt(self, title, prompt, default = ""):
		try:
			self.inputBox = InputBox(self, title, prompt, default)
		except:
			self.warn_insufficient_screen_space()
			raise

		response = self.inputBox.show()
		self.main_window.repaint()
		return response

	# checks if buffer is up-to-date with file on disk
	def is_file_already_loaded(self, filename):
		return self.buffers.does_file_have_its_own_buffer(filename)

	# prints warning to user that the screen dimensions are below the minimum requirement
	def warn_insufficient_screen_space(self):
		self.main_window.repaint(f"error: insufficient screen space (minimum reqd.: {MIN_WIDTH}x{MIN_HEIGHT} ), ash may crash unexpectedly")
		beep()
		time.sleep(1)

	# returns the appropriate app title
	def get_app_title(self, active_editor = None):
		app_title = ""

		if(active_editor == None):
			if(self.app_mode == APP_MODE_PROJECT):
				app_title = "[" + get_file_title(self.project_dir) + "]"
				return app_title
			else:
				return app_title

		if(self.app_mode == APP_MODE_FILE):
			app_title = get_file_title(active_editor.buffer.get_name())
		elif(self.app_mode == APP_MODE_PROJECT):
			if(active_editor.buffer.filename == None):
				app_title = active_editor.buffer.get_name()
			else:
				app_title = get_relative_file_title(self.project_dir, active_editor.buffer.filename)
		
		app_title = ("  " if active_editor.buffer.save_status else UNSAVED_BULLET + " ") + app_title
		return app_title