# ---------------------------------------------------------------------------------------------
#  Copyright (c) Akash Nag. All rights reserved.
#  Licensed under the MIT License. See LICENSE.md in the project root for license information.
# ---------------------------------------------------------------------------------------------

# This module implements a TopLevel window, which always spans the entire screen
# An instance of Ash should contain exactly 1 TopLevel window visible at any given time

from ash import *

from ash.gui import *
from ash.gui.windowManager import *
from ash.gui.statusbar import *
from ash.gui.window import *
from ash.core.bufferManager import *
from ash.core.gitRepo import *

# <-------------------- class declaration --------------->
class TopLevelWindow(Window):
	def __init__(self, app, stdscr, title, handler_func):
		super().__init__(0, 0, 0, 0, title)
		self.app = app
		self.win = stdscr
		self.handler_func = handler_func
		self.app_name = self.app.get_app_name()		

		# status-bar sections: total=101+1 (min)
		# *status (8), *file-type (11), encoding(7), sloc (20), file-size (10), 
		# *unsaved-file-count (4), *tab-size (1), cursor-position (6+1+6+3+8=24)
		self.status = StatusBar(self, [ 10, 13, 9, 22, 12, 6, 3, -1 ])
		self.window_manager = WindowManager(self.app, self)

	def update_status(self):
		aed = self.window_manager.get_active_editor()

		tab_size = ""
		language = ""
		editor_state = "inactive"
		cursor_position = ""
		loc_count = ""
		file_size = ""
		unsaved_file_count = ""
		encoding = ""

		if(aed != None):
			lines, sloc = aed.buffer.get_loc()
			loc_count = str(lines) + " lines (" + str(sloc) + " sloc)"
			
			if(aed.buffer.filename != None):
				if(os.path.isfile(aed.buffer.filename)): file_size = aed.buffer.get_file_size()
				
				language = get_textfile_mimetype(aed.buffer.filename)
				
				if(aed.buffer.save_status):
					editor_state = "saved"
				else:
					editor_state = "modified"
			else:
				editor_state = "unsaved"
				language = "unknown"

			cursor_position = str(aed.get_cursor_position()) + aed.get_selection_length_as_string()
			encoding = aed.buffer.encoding
			tab_size = str(aed.tab_size)
		
		unsaved_file_count = str(self.app.buffers.get_unsaved_count()) + "*"
		
		if(self.app.app_mode == APP_MODE_PROJECT):			
			if(GitRepo.has_repo_in_dir(self.app.project_dir)):
				editor_state = GitRepo.get_active_branch_name(self.app.project_dir)

		self.status.set(0, editor_state)
		self.status.set(1, language)
		self.status.set(2, encoding)
		self.status.set(3, loc_count)
		self.status.set(4, file_size)		
		self.status.set(5, unsaved_file_count)
		self.status.set(6, tab_size)
		self.status.set(7, cursor_position, "right")
				
		if(aed != None):
			self.set_title(self.app.get_app_title(aed))
		else:
			self.set_title(self.app.get_app_title())
	
	# shows the window and starts the event-loop
	def show(self, welcome_msg = None):
		curses.curs_set(False)
		self.win.keypad(True)
		self.win.timeout(0)
		self.repaint(welcome_msg)

		while(self.win != None):
			ch = self.win.getch()
			if(ch == -1): continue
			
			# send Ctrl/Fn keypresses to main handler first
			if(self.handler_func != None):
				ch = self.handler_func(ch)
				if(self.win == None): return

			if(ch == -1): continue
			
			aed = self.get_active_editor()
			if(aed != None): aed.focus()
			
			if(aed != None):
				aed.perform_action(ch)
				self.repaint()
	
	# repaint background
	def repaint_background(self):
		self.win.addstr(0, 0, " " * self.width, gc("titlebar"))
		for i in range(1, self.height-1):
			self.win.addstr(i, 0, " " * self.width, gc("background"))
		self.win.addstr(self.height-1, 0, " " * (self.width - 1), gc("background"))

	# draws the window
	def repaint(self, error_msg = None, caller=None):
		curses.curs_set(False)
		if(self.win == None): return
		
		self.update_status()
		self.readjust()
		self.win.clear()
		self.repaint_background()

		if(error_msg == None):
			if(self.status != None): self.status.repaint(self.win, self.width-1, self.height-1, 0)
		else:
			if(len(error_msg) + 1 > self.width - 1): error_msg = error_msg[0:self.width-2]
			self.win.addstr(self.height-1, 0, (" " + error_msg).ljust(self.width-1), gc("messagebox-background"))
		
		try:
			if(len(self.title) == 0):
				self.win.addstr(0, 0, self.app_name.center(self.width), curses.A_BOLD | gc("titlebar"))
			else:
				title_text = self.title + " - " + self.app_name		
				ts = (self.width - len(title_text)) // 2
				self.win.addstr(0, ts, self.title + " - ", gc("titlebar"))
				self.win.addstr(0, ts + len(self.title + " - "), self.app_name, curses.A_BOLD | gc("titlebar"))

			self.window_manager.repaint()
		except:
			raise
		
		self.win.refresh()

	# driver function
	def addstr(self, y, x, text, style):
		self.win.addstr(y, x, text, style)

	def bottom_up_readjust(self):				# called from WindowManager
		self.app.readjust()

	def readjust(self):							# called from AshEditorApp
		if(self.height == self.app.screen_height and self.width == self.app.screen_width): return
		self.height, self.width = self.app.screen_height, self.app.screen_width
		self.window_manager.readjust()

	def invoke_activate_editor(self, buffer_id, buffer):
		aed = self.get_active_editor()
		if(aed == None):
			self.add_tab_with_buffer(buffer_id, buffer)
		else:
			aed.set_buffer(buffer_id, buffer)
		self.repaint()

	def toggle_filename_visibility(self):
		self.window_manager.toggle_filename_visibility()
		self.repaint()

	# <------------------------------------ stub functions ------------------------------->

	def get_editor_count(self):
		return self.window_manager.get_editor_count()

	def close_active_editor(self):
		self.window_manager.close_active_editor()
		self.repaint()

	def close_all_except_active_editor(self):
		self.window_manager.close_all_except_active_editor()
		self.repaint()

	def add_blank_tab(self):
		self.window_manager.add_blank_tab()
		self.repaint()

	def add_tab_with_buffer(self, bid, buffer):
		self.window_manager.add_tab_with_buffer(bid, buffer)
		self.repaint()

	def remove_tab(self, tab_index):
		self.window_manager.remove_tab(tab_index)
		self.repaint()

	def close_active_tab(self):
		self.window_manager.close_active_tab()
		self.repaint()

	def get_tabs_info(self):
		return self.window_manager.get_tabs_info()

	def get_tab_count(self):
		return self.window_manager.get_tab_count()

	def switch_to_tab(self, tab_index):
		self.window_manager.switch_to_tab(tab_index)
		self.repaint()

	def switch_to_next_tab(self):
		self.window_manager.switch_to_next_tab()
		self.repaint()

	def switch_to_previous_tab(self):
		self.window_manager.switch_to_previous_tab()
		self.repaint()

	def get_active_editor(self):
		return self.window_manager.get_active_editor()

	def switch_to_next_editor(self):
		self.window_manager.switch_to_next_editor()
		self.repaint()

	def switch_to_previous_editor(self):
		self.window_manager.switch_to_previous_editor()
		self.repaint()

	def split_horizontally(self):
		self.window_manager.split_horizontally()
		self.repaint()

	def split_vertically(self):
		self.window_manager.split_vertically()
		self.repaint()

	def merge_horizontally(self):
		self.window_manager.merge_horizontally()
		self.repaint()
	
	def merge_vertically(self):
		self.window_manager.merge_vertically()
		self.repaint()

	def get_active_tab(self):
		return self.window_manager.get_active_tab()

	def get_active_tab_index(self):
		return self.window_manager.get_active_tab_index()

	def reload_active_buffer_from_disk(self):
		self.window_manager.reload_active_buffer_from_disk()
		self.repaint()

	def save_and_close_active_editor(self):
		aed = self.window_manager.get_active_editor()
		if(aed != None): aed.keyHandler.save_and_close()

	def save_active_editor(self):
		aed = self.window_manager.get_active_editor()
		if(aed != None): aed.keyHandler.handle_save()