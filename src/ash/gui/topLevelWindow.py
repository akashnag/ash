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
#from ash.gui.layoutManager import *
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

		# <--------------- new ------------------->
		self.window_manager = WindowManager(self.app, self)

		#self.layout_manager = LayoutManager(self)		
		#self.layout_type = LAYOUT_SINGLE
		#self.active_editor_index = -1
		#self.editors = list()
		#for i in range(6): self.editors.append(None)
	
	# sets layout
	#def set_layout(self, layout_type):
	#	self.layout_manager.set_layout(layout_type)
	#	self.layout_manager.readjust()

	
	# returns the active editor object
	#def get_active_editor(self):
	#	if(self.active_editor_index < 0):
	#		return None
	#	else:
	#		if(self.editors[self.active_editor_index] == None):
	#			self.active_editor_index = -1
	#			return None
	#		else:
	#			return self.editors[self.active_editor_index]

	# closes the active editor
	#def close_active_editor(self):
	#	# no active editor: return: nothing to do
	#	if(self.active_editor_index < 0): return
	#
	#	# close active editor
	#	self.editors[self.active_editor_index].destroy()
	#	self.editors[self.active_editor_index] = None
	#	self.active_editor_index = -1
	#
	#	# switch to a different editor (if available)
	#	n = len(self.editors)
	#	for i in range(n):
	#		if(self.editors[i] != None):
	#			self.layout_manager.invoke_activate_editor(i)
	#			break
	#
	#	# repaint
	#	self.repaint()

	def update_status(self):
		#aed = self.get_active_editor()
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

		#aed = None
		#if(self.editors[0] != None): 
		#	aed = self.editors[0]
		# 	aed.focus()
		
		# <------------------- new -------------------->
		
		# ----------------------------------------------

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
		
	# draws the window
	def repaint(self, error_msg = None, caller=None):
		curses.curs_set(False)
		if(self.win == None): return
		
		self.update_status()
		self.readjust()
		self.win.clear()

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

			#self.layout_manager.draw_layout_borders()
			#self.layout_manager.repaint_editors(caller=caller)
			self.window_manager.repaint()
		except:
			raise
		
		self.win.refresh()

	# driver function
	def addstr(self, y, x, text, style):
		self.win.addstr(y, x, text, style)

	# <------------------------ called from dialogbox handlers -------------------------------->
	#def get_first_free_editor_index(self, barring = -1):
	#	n = len(self.editors)
	#	ec = EDITOR_COUNTS[self.layout_type]
	#
	#	for i in range(n):
	#		if(i >= ec): continue
	#		if(i != barring and self.editors[i] == None): return i
	#	return -1

	#def get_visible_editor_count(self):
	#	count = 0
	#	for i in range(len(self.editors)):
	#		if(self.editors[i] != None): count += 1
	#	return count

	def bottom_up_readjust(self):				# called from WindowManager
		self.app.readjust()

	def readjust(self):							# called from AshEditorApp
		if(self.height == self.app.screen_height and self.width == self.app.screen_width): return
		self.height, self.width = self.app.screen_height, self.app.screen_width
		self.window_manager.readjust()

	def invoke_activate_editor(self, buffer_id, buffer):
		pass		# ADD CODE

	# <------------------------------------ stub functions ------------------------------->

	def get_editor_count(self):
		return self.window_manager.get_editor_count()

	def close_active_editor(self):
		self.window_manager.close_active_editor()
		self.repaint()

	def add_tab(self):
		self.window_manager.add_tab()
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