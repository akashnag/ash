# ---------------------------------------------------------------------------------------------
#  Copyright (c) Akash Nag. All rights reserved.
#  Licensed under the MIT License. See LICENSE.md in the project root for license information.
# ---------------------------------------------------------------------------------------------

# This is main app class

from ash import *

import time
import signal

from ash.core.bufferManager import *
from ash.core.logger import *

from ash.utils.utils import *
from ash.utils.keyUtils import *
from ash.utils.fileUtils import *
from ash.utils.commandUtils import *
from ash.utils.keyMappingsManager import *
from ash.utils.settingsManager import *

from ash.formatting.colors import *
from ash.formatting.formatting import *
from ash.formatting.themeManager import *

from ash.gui.topLevelWindow import *
from ash.gui.msgBox import *
from ash.gui.inputBox import *
from ash.gui.dialogHandler import *
from ash.gui.fileLoader import *

class AshEditorApp:
	def __init__(self, ash_dir, args):
		self.ash_dir = ash_dir
		self.args = args
		self.argc = len(args)
		self.supports_colors = True
		self.dialog_handler = DialogHandler(self)

		# create the application data directory
		if(not os.path.exists(APP_DATA_DIR)): os.mkdir(APP_DATA_DIR)
		if(not os.path.exists(APP_PLUGINS_DIR)): os.mkdir(APP_PLUGINS_DIR)
		if(not os.path.exists(APP_KEYMAPS_DIR)): os.mkdir(APP_KEYMAPS_DIR)
		if(not os.path.exists(APP_THEMES_DIR)): os.mkdir(APP_THEMES_DIR)

		log_init()
		
	
	def open_project(self, progress_handler = None, ask_to_restore_session = True):
		# add project path to recent record
		self.session_storage.add_opened_file_to_record(self.project_dir)

		# find all files
		all_files = glob.glob(self.project_dir + "/**/*", recursive=True)

		# reset the settings
		self.settings_manager = SettingsManager(self)

		# create buffers for each file
		for i, f in enumerate(all_files):
			if(not os.path.isfile(f)): continue
			if(should_ignore_file(f)): continue
			if(BufferManager.is_binary(f)): continue
			has_backup = BufferManager.backup_exists(f)
			if(not self.buffers.does_file_have_its_own_buffer(f)):
				self.buffers.create_new_buffer(filename=f, has_backup=has_backup)
			if(progress_handler != None): 
				progress = ( ( i / len(all_files) ) * 100 )
				progress_handler("Loading...", progress)

		# check if session exists, ask user if they want to restore it
		if(ask_to_restore_session and self.session_storage.does_project_have_saved_session(self.project_dir)):
			if(self.ask_question("RESTORE SESSION", "Do you want to restore the session for this project?")):
				self.session_storage.set_project_session(self.project_dir)

		# complete load process
		if(progress_handler != None): progress_handler("Ready", None)
		
	def open_files_from_commandline_args(self, progress_handler = None):
		for i in range(1, len(self.args)):
			if(os.path.isdir(self.args[i])): continue			
			filePath = str(os.path.abspath(self.args[i]))
			if(BufferManager.is_binary(filePath)): continue
			has_backup = BufferManager.backup_exists(filePath)
			if(not self.buffers.does_file_have_its_own_buffer(filePath)):
				self.buffers.create_new_buffer(filename=filePath, has_backup=has_backup)
			if(progress_handler != None): 
				progress = ( ( i / (len(self.args)-1) ) * 100 )
				progress_handler("Loading...", progress)
		if(progress_handler != None): progress_handler("Ready", None)

	def load_files(self, progress_handler = None):
		if(self.argc == 1):
			self.app_mode = APP_MODE_FILE
			
			# SettingsManager must be initialized after setting of app_mode property
			self.settings_manager = SettingsManager(self)
		
			# data is piped: will hang due to not processing EOF
			# no solution found :(
		elif(self.argc == 2 and os.path.isdir(self.args[1])):			
			self.app_mode = APP_MODE_PROJECT
			self.project_dir = str(os.path.abspath(self.args[1]))

			# SettingsManager must be initialized after setting of app_mode property
			self.settings_manager = SettingsManager(self)
		
			self.open_project(progress_handler)
		else:
			self.app_mode = APP_MODE_FILE
		
			# SettingsManager must be initialized after setting of app_mode property
			self.settings_manager = SettingsManager(self)
		
			self.open_files_from_commandline_args(progress_handler)

		
	def run(self):
		if(self.argc >= 2):
			if(self.args[1] == "--help"):
				self.print_help()
				return 0
			elif(self.args[1] == "--version"):
				self.print_version()
				return 0
		
		ret_code = curses.wrapper(self.app_main)
		return ret_code

	def print_help(self):
		print("Usage:\tash\n      \t\t(opens a blank buffer for editing)")
		print(" or   \tash <filepath>...\n      \t\t(opens one or more specified files for editing)")
		print(" or   \tash <path-to-directory>\n      \t\t(opens the specified directory)")
		print(" or   \tash --help\n      \t\t(prints this help)")
		print(" or   \tash --version\n      \t\t(prints the current version)")
		
	def print_version(self):
		print("Ash: a modern terminal text-editor")
		print("Version: " + ash.__version__ + " (build: " + ash.__build__ + ")")
		print("Released: " + ash.__release_date__)
		print(ash.APP_COPYRIGHT_TEXT)
		print(ash.APP_LICENSE_TEXT)

	# recalculates screen dimensions
	def readjust(self):
		self.screen_height, self.screen_width = self.stdscr.getmaxyx()
		self.main_window.readjust()
		return (self.screen_height, self.screen_width)

	# returns the version of Ash
	def get_app_version(self):
		return str(ash.__version__) + str(ash.__build__)

	# returns the name of the application
	def get_app_name(self):
		return "ash-" + self.get_app_version()
	
	# initialize the GUI
	def app_main(self, stdscr):
		# initialize screen
		self.stdscr = stdscr
		self.screen_height, self.screen_width = self.stdscr.getmaxyx()				
		curses.raw()
		curses.mousemask(curses.ALL_MOUSE_EVENTS)
		
		# create manager objects
		self.buffers = BufferManager(self)
		self.theme_manager = ThemeManager(self)
		self.key_mappings_manager = KeyMappingsManager(self)
		
		# create the Main Window and session storage objects
		self.main_window = TopLevelWindow(self, self.stdscr, "ash " + self.get_app_version(), self.main_key_handler)
		self.session_storage = SessionStorage(self, self.main_window.window_manager, self.buffers)
		
		# create command interpreter object
		self.command_interpreter = CommandInterpreter(self, self.main_window)

		# adjust sizes
		self.readjust()

		# load files
		self.load_files(self.progress_handler)
		
		if(self.app_mode == APP_MODE_FILE):
			if(len(self.buffers) > 0):
				bid = 0
				buffer = self.buffers.get_buffer_by_id(bid)
				self.main_window.add_tab_with_buffer(bid, buffer)				
			elif(len(self.buffers) == 0):
				self.main_window.add_blank_tab()
		
		welcome_msg = f"ash-{self.get_app_version()} | F1: Help"
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
		# Keep the following code for diagnostic purposes:
		#if(not KeyBindings.is_key(ch, "FORCE_QUIT") and self.show_error("You pressed: " + str(curses.keyname(ch)))):
		#	self.main_window.repaint()
		#	return -1
		
		# NOTE: whenever a key-combo is being handled here that may also be triggered
		# in an active editor (e.g. Ctrl+O), always:
		#	(i) add a check in the condition to ensure no active editors exist
		#	(ii) and, return -1 to prevent it being handled again if a new active editor
		#		 is created in the process of the handling

		if(KeyBindings.is_key(ch, "FORCE_QUIT")): 
			# force quits the app without saving
			self.dialog_handler.invoke_forced_quit()
			return -1
		elif(KeyBindings.is_key(ch, "CLOSE_EDITOR")):
			# quits the active editor or the active tab (if no editor is active) or the app (if no tab is active)
			self.dialog_handler.invoke_quit()
			return -1
		elif(KeyBindings.is_key(ch, "RESIZE_WINDOW")):
			self.readjust()
			self.main_window.repaint()
			return -1
		elif(KeyBindings.is_key(ch, "SHOW_ACTIVE_TABS")):
			self.dialog_handler.invoke_show_active_tabs()
			return -1
		elif(KeyBindings.is_key(ch, "LIST_ACTIVE_BUFFERS")):
			self.dialog_handler.invoke_list_active_files()
			return -1
		elif(self.app_mode == APP_MODE_PROJECT and KeyBindings.is_key(ch, "SHOW_PROJECT_EXPLORER")):
			# project explorer
			self.dialog_handler.invoke_project_explorer()
			return -1
		elif(KeyBindings.is_key(ch, "NEW_BUFFER") and self.main_window.get_active_editor() == None):
			# file-new
			self.dialog_handler.invoke_file_new()
			return -1
		elif(KeyBindings.is_key(ch, "OPEN_FILE") and self.main_window.get_active_editor() == None):
			# file-open
			self.dialog_handler.invoke_file_open()
			return -1		
		if(KeyBindings.is_key(ch, "SHOW_HELP")):
			self.dialog_handler.invoke_help_key_bindings()
			return -1
		elif(KeyBindings.is_key(ch, "SHOW_RECENT_FILES")):
			self.dialog_handler.invoke_recent_files()
			return -1
		elif(KeyBindings.is_key(ch, "SWITCH_TO_PREVIOUS_EDITOR")):
			self.main_window.switch_to_previous_editor()
			return -1
		elif(KeyBindings.is_key(ch, "SWITCH_TO_NEXT_EDITOR")):
			self.main_window.switch_to_next_editor()
			return -1
		elif(KeyBindings.is_key(ch, "SWITCH_TO_PREVIOUS_TAB")):
			self.main_window.switch_to_previous_tab()
			return -1
		elif(KeyBindings.is_key(ch, "SWITCH_TO_NEXT_TAB")):
			self.main_window.switch_to_next_tab()
			return -1
		elif(KeyBindings.is_key(ch, "TOGGLE_FILENAMES_IN_EDITORS")):
			self.main_window.toggle_filename_visibility()
			return -1
		elif(KeyBindings.is_key(ch, "CREATE_NEW_TAB")):
			self.main_window.add_blank_tab()
			return -1	
		elif(KeyBindings.is_key(ch, "SPLIT_HORIZONTALLY")):
			self.main_window.split_horizontally()
			return -1
		elif(KeyBindings.is_key(ch, "SPLIT_VERTICALLY")):
			self.main_window.split_vertically()
			return -1
		elif(KeyBindings.is_key(ch, "MERGE_HORIZONTALLY")):
			self.main_window.merge_horizontally()
			return -1
		elif(KeyBindings.is_key(ch, "MERGE_VERTICALLY")):
			self.main_window.merge_vertically()
			return -1
		elif(KeyBindings.is_key(ch, "CLOSE_ALL_EXCEPT_ACTIVE_EDITOR")):
			self.main_window.close_all_except_active_editor()
			return -1
		elif(KeyBindings.is_key(ch, "SHOW_PROJECT_FIND")):
			self.dialog_handler.invoke_project_find()
			return -1
		elif(KeyBindings.is_key(ch, "SHOW_PROJECT_FIND_AND_REPLACE")):
			self.dialog_handler.invoke_project_find_and_replace()
			return -1
		elif(KeyBindings.is_key(ch, "SHOW_COMMAND_WINDOW")):
			self.dialog_handler.invoke_command_palette()
			return -1
		elif(KeyBindings.is_key(ch, "SHOW_THEME_MANAGER")):
			self.dialog_handler.invoke_theme_manager()
			return -1
		elif(KeyBindings.is_key(ch, "SHOW_ABOUT")):
			self.dialog_handler.invoke_help_about()
			return -1
		elif(KeyBindings.is_key(ch, "EDIT_PROJECT_SETTINGS")):
			self.dialog_handler.invoke_project_settings()
			return -1
		elif(KeyBindings.is_key(ch, "EDIT_GLOBAL_SETTINGS")):
			self.dialog_handler.invoke_global_settings()
			return -1
		elif(KeyBindings.is_key(ch, "COMPILE_ACTIVE_FILE")):
			self.main_window.compile_current_file()
			return -1
		elif(KeyBindings.is_key(ch, "EXECUTE_ACTIVE_FILE")):
			self.main_window.execute_current_file()
			return -1
		elif(KeyBindings.is_key(ch, "BUILD_PROJECT")):
			self.main_window.build_current_project()
			return -1
		elif(KeyBindings.is_key(ch, "EXECUTE_PROJECT")):
			self.main_window.execute_current_project()
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
	def prompt(self, title, prompt, default = "", width = 0):
		try:
			self.inputBox = InputBox(self, title, prompt, default, width)
		except:
			self.warn_insufficient_screen_space()
			raise

		response = self.inputBox.show()
		self.main_window.repaint()
		return response

	def load_file(self, filename, encoding):
		try:
			self.fileLoader = FileLoader(self, filename, encoding)
		except:
			self.warn_insufficient_screen_space()
			raise

		data = self.fileLoader.load()
		self.main_window.repaint()
		return data

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

		return self.get_displayed_file_title(active_editor)
		
	def get_displayed_file_title(self, active_editor):
		if(self.app_mode == APP_MODE_FILE):
			app_title = get_file_title(active_editor.buffer.get_name())
		elif(self.app_mode == APP_MODE_PROJECT):
			if(active_editor.buffer.filename == None):
				app_title = active_editor.buffer.get_name()
			else:
				app_title =  get_relative_file_title(self.project_dir, active_editor.buffer.filename)
		app_title = ("  " if active_editor.buffer.save_status else UNSAVED_BULLET + " ") + app_title
		return app_title