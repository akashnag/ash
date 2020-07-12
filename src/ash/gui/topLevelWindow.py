# ---------------------------------------------------------------------------------------------
#  Copyright (c) Akash Nag. All rights reserved.
#  Licensed under the MIT License. See LICENSE.md in the project root for license information.
# ---------------------------------------------------------------------------------------------

# This module implements a TopLevel window, which always spans the entire screen
# Ideally, an instance of Ash should contain exactly 1 TopLevel window visible at any given time

from ash.gui import *
from ash.gui.window import *
from ash.gui.layoutManager import *
from ash.core.bufferManager import *

# <-------------------- class declaration --------------->
class TopLevelWindow(Window):
	def __init__(self, app, stdscr, title, handler_func):
		super().__init__(0, 0, 0, 0, title)
		self.layout_manager = LayoutManager(self)
		self.app = app
		self.win = stdscr
		self.handler_func = handler_func
		self.layout_type = LAYOUT_SINGLE
		self.app_name = self.app.get_app_name()
		self.active_editor_index = -1

		self.editors = list()
		for i in range(6): self.editors.append(None)
	
	# sets layout
	def set_layout(self, layout_type):
		self.layout_manager.set_layout(layout_type)
		self.layout_manager.readjust()

	# adds a status bar
	def add_status_bar(self, status):
		self.status = status

	# returns the statusbar widget if any
	def get_status_bar(self):
		return self.status
	
	# returns the active editor object
	def get_active_editor(self):
		if(self.active_editor_index < 0):
			return None
		else:
			if(self.editors[self.active_editor_index] == None):
				self.active_editor_index = -1
				return None
			else:
				return self.editors[self.active_editor_index]

	# closes the active editor
	def close_active_editor(self):
		# no active editor: return: nothing to do
		if(self.active_editor_index < 0): return

		# close active editor
		self.editors[self.active_editor_index].destroy()
		self.editors[self.active_editor_index] = None
		self.active_editor_index = -1

		# switch to a different editor (if available)
		n = len(self.editors)
		for i in range(n):
			if(self.editors[i] != None):
				self.layout_manager.invoke_activate_editor(i)
				break

		# repaint
		self.repaint()

	def update_status(self):
		aed = self.get_active_editor()

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

		if(self.editors[0] != None): self.editors[0].focus()

		while(True):
			ch = self.win.getch()
			if(ch == -1): continue
			
			# send Ctrl/Fn keypresses to main handler first
			if(self.handler_func != None):# and is_ctrl_or_func(ch)):
				ch = self.handler_func(ch)
				if(self.win == None): return

			if(ch == -1): continue
			
			if(self.active_editor_index > -1):
				self.get_active_editor().perform_action(ch)

			self.repaint()
		
	# draws the window
	def repaint(self, error_msg = None):
		curses.curs_set(False)
		if(self.win == None): return
		
		self.update_status()
		self.layout_manager.readjust()
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

			self.layout_manager.draw_layout_borders()
			self.layout_manager.repaint_editors()
		except:
			pass
		
		self.win.refresh()

	# <------------------------ called from dialogbox handlers -------------------------------->
	def get_first_free_editor_index(self, barring = -1):
		n = len(self.editors)
		ec = EDITOR_COUNTS[self.layout_type]

		for i in range(n):
			if(i >= ec): continue
			if(i != barring and self.editors[i] == None): return i
		return -1

	def get_visible_editor_count(self):
		count = 0
		for i in range(len(self.editors)):
			if(self.editors[i] != None): count += 1
		return count