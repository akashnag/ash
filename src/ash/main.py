# ---------------------------------------------------------------------------------------------
#  Copyright (c) Akash Nag. All rights reserved.
#  Licensed under the MIT License. See LICENSE.md in the project root for license information.
# ---------------------------------------------------------------------------------------------

# This is main app class

from ash import *

from ash.core.bufferManager import *
from ash.core.logger import *
from ash.core.fileData import *
from ash.core.utils import *
from ash.core.dataUtils import *

from ash.formatting.colors import *
from ash.formatting.formatting import *

from ash.gui.topLevelWindow import *
from ash.gui.editor import *
from ash.gui.statusbar import *
from ash.gui.msgBox import *
from ash.gui.dialogHandler import *

APP_VERSION			= "0.1.0-dev"
UNSAVED_BULLET		= "\u2022"

APP_MODE_FILE		= 1		# if ash is invoked with zero or more file names
APP_MODE_PROJECT	= 2		# if ash is invoked with a single directory name

class AshEditorApp:
	def __init__(self, ash_dir, args):
		self.ash_dir = ash_dir
		self.args = args
		self.argc = len(args)
		self.dialog_handler = DialogHandler(self)

		self.ignore_screen_size = False
		if(self.argc > 1 and self.args[1] == "--i"):
			self.ignore_screen_size = True
			self.args.pop(1)
			self.argc -= 1

		log_init()
		read_file_associations(self)
		
	def run(self):
		self.buffers = BufferManager()
		
		if(self.argc == 1):
			self.app_mode = APP_MODE_FILE
		elif(self.argc == 2 and os.path.isdir(self.args[1])):
			self.app_mode = APP_MODE_PROJECT			
			self.project_dir = str(pathlib.Path(self.args[1]).absolute())
			all_files = glob.glob(self.project_dir + "/**/*.*", recursive=True)
			for f in all_files:
				if(f.find("/__pycache__/") == -1): 
					has_backup = BufferManager.backup_exists(f)
					self.buffers.create_new_buffer(filename=f, has_backup=has_backup)
		else:
			self.app_mode = APP_MODE_FILE
			for i in range(1, len(self.args)):
				if(os.path.isdir(self.args[i])):
					print("ERROR: cannot open more than 1 project")
					return
				filePath = str(pathlib.Path(self.args[i]).absolute())
				has_backup = BufferManager.backup_exists(filePath)
				self.buffers.create_new_buffer(filename=filePath, has_backup=has_backup)
		
		# invoke the GUI initialization routine
		ret_code = curses.wrapper(self.app_main)
		if(ret_code == -1):
			print("Error: screen-size insufficient, required at least: 102 x 20")
			print("To ignore screen limitations: restart with --i as the first argument")

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
			app_title = get_relative_file_title(self.project_dir, active_editor.buffer.filename)
		
		app_title = ("  " if active_editor.save_status else UNSAVED_BULLET + " ") + app_title
		return app_title

	# initialize the GUI
	def app_main(self, stdscr):
		self.stdscr = stdscr
		self.readjust()

		if(not self.ignore_screen_size and (self.screen_width < 102 or self.screen_height < 20)):
			return -1
		
		init_colors()
		curses.raw()
		
		self.main_window = TopLevelWindow(self, self.stdscr, "Ash " + APP_VERSION, self.main_key_handler)
		
		# status-bar sections: total=101+1 (min)
		# *status (8), *file-type (11), encoding(7), sloc (20), file-size (10), 
		# *unsaved-file-count (4), *tab-size (1), cursor-position (6+1+6+3+8=24)
		self.main_window.add_status_bar(StatusBar(self.main_window, [ 10, 13, 9, 22, 12, 6, 3, -1 ]))
		
		if(self.app_mode != APP_MODE_PROJECT):
			editor = Editor(self.main_window)
			if(len(self.buffers) == 0): 
				bid, buffer = self.buffers.create_new_buffer()
			else:
				bid = 0
				buffer = self.buffers.get_buffer_by_id(bid)
							
			editor.set_buffer(bid, buffer)			
			self.main_window.add_editor(editor)
			self.main_window.layout_manager.readjust(True)
		
		self.main_window.show()		# this call returns when main_window() is closed
		self.__destroy()
		return 0
	
	# called on app_exit
	def __destroy(self):
		pass

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
		elif(ch == curses.KEY_RESIZE):
			self.main_window.repaint()
		elif(is_ctrl(ch, "L")):
			# adjust layout
			self.dialog_handler.invoke_switch_layout()
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
		self.msgBox = MessageBox(self, ("ERROR" if error else "INFORMATION"), msg)
		while(True):
			response = self.msgBox.show()
			if(response == MSGBOX_OK): 
				self.main_window.repaint()
				return -1
			beep()

	# displays a question
	def ask_question(self, title, question, hasCancel=False):
		self.msgBox = MessageBox(self, title, question, (MSGBOX_TYPE_YES_NO_CANCEL if hasCancel else MSGBOX_TYPE_YES_NO))
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
		return self.buffers.does_file_have_its_own_buffer(filename)