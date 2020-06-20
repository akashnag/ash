# ---------------------------------------------------------------------------------------------
#  Copyright (c) Akash Nag. All rights reserved.
#  Licensed under the MIT License. See LICENSE.md in the project root for license information.
# ---------------------------------------------------------------------------------------------

# This module implements a TopLevel window, which always spans the entire screen
# Ideally, an instance of Ash should contain exactly 1 TopLevel window visible at any given time

from ash.widgets import *
from ash.widgets.window import *
from ash.widgets.utils.utils import *
from ash.widgets.utils.formatting import *

# <------------------- constants -------------------->
SPLIT_TYPE_NONE 		= 0
SPLIT_TYPE_HORIZONTAL	= 1
SPLIT_TYPE_VERTICAL		= 2

HORIZONTAL_BORDER_SYMBOL= "\u2500"
VERTICAL_BORDER_SYMBOL	= "\u2502"

# <-------------------- class declaration --------------->
class TopLevelWindow(Window):
	def __init__(self, stdscr, title, handler_func):
		height, width = stdscr.getmaxyx()
		super().__init__(0, 0, height, width, title)
		self.win = stdscr
		self.handler_func = handler_func
		self.split = SPLIT_TYPE_NONE
		self.split_pos = -1
		self.editor1 = None
		self.editor2 = None
		self.active_editor_index = 0
			
	# initialize editors
	def set_editors(self, ed1, ed2):
		self.editor1 = ed1
		self.editor2 = ed2
		self.active_editor_index = 1

	# load data for editor
	def set_editor_data(self, index, data):
		if(index == 1 and self.editor1 != None):
			self.editor1.set_data(data)
		elif(index == 2 and self.editor2 != None):
			self.editor2.set_data(data)

	# sets split mode
	def set_split(self, split_type, split_pos = -1):
		self.split = split_type
		self.split_pos = split_pos

	# adds a status bar
	def add_status_bar(self, status):
		self.status = status

	# returns the statusbar widget if any
	def get_status_bar(self):
		return self.status
	
	# returns the active editor object
	def get_active_editor(self):
		if(self.active_editor_index < 1):
			return None
		elif(self.active_editor_index == 1):
			return self.editor1
		elif(self.active_editor_index == 2):
			return self.editor2
		else:
			return None

	def update_status(self):
		aed = self.get_active_editor()

		language = "None"
		editor_state = "Inactive"
		cursor_position = ""
		loc_count = ""
		file_size = "0 bytes"

		if(aed != None):
			lines, sloc = aed.get_loc()
			loc_count = str(lines) + " lines (" + str(sloc) + " sloc)"
			
			if(aed.has_been_allotted_file):
				if(os.path.isfile(aed.filename)): file_size = aed.get_file_size()
				language = get_file_type(aed.filename)
				if(language == None): language = "Unknown"
				if(aed.save_status):
					editor_state = "Saved"
				else:
					editor_state = "Modified"
			else:
				editor_state = "Unsaved"
				language = "Unknown"

			cursor_position = str(aed.get_cursor_position())
		
		self.status.set(0, editor_state)
		self.status.set(1, language)
		self.status.set(2, loc_count)
		self.status.set(3, file_size)
		self.status.set(4, cursor_position)
		

	# shows the window and starts the event-loop
	def show(self):
		curses.curs_set(False)
		self.win.keypad(True)
		self.win.timeout(0)
		
		self.repaint()	
		while(True):
			ch = self.win.getch()
			if(ch == -1): continue
			
			# send keypresses to main handler first
			# ideally only Ctrl/Func key combinations should be sent
			if(self.handler_func != None):
				ch = self.handler_func(ch)
				if(self.win == None): return
			
			if(self.active_widget_index < 0 or not self.get_active_widget().does_handle_tab()):
				if((is_tab(ch) or ch == curses.KEY_BTAB)):
					old_index = self.active_widget_index
					if(is_tab(ch)):
						self.active_widget_index = self.get_next_focussable_widget_index()
					elif(ch == curses.KEY_BTAB):
						self.active_widget_index = self.get_previous_focussable_widget_index()
					
					if(old_index != self.active_widget_index):
						if(old_index > -1): self.widgets[old_index].blur()
						if(self.active_widget_index > -1): self.widgets[self.active_widget_index].focus()

					ch = -1

			if(ch > -1 and self.active_editor_index > 0):
				self.get_active_editor().perform_action(ch)

			self.repaint()
			
	# check if terminal window has been resized, if so, readjust
	def readjust(self):
		h, w = self.win.getmaxyx()
		if(h != self.height or w != self.width):
			self.height, self.width = h, w
			for w in self.widgets:
				w.readjust()

	# draws the window
	def repaint(self):
		if(self.win == None): return
		
		self.update_status()
		self.readjust()
		self.win.clear()

		self.win.addstr(0, 0, pad_center_str(self.title, self.width), curses.A_BOLD | gc(COLOR_TITLEBAR))
		if(self.status != None): self.win.addstr(self.height-1, 0, str(self.status), gc(COLOR_STATUSBAR))

		if(self.split != SPLIT_TYPE_NONE):
			if(self.split == SPLIT_TYPE_HORIZONTAL):
				self.win.addstr(self.height//2, 0, HORIZONTAL_BORDER_SYMBOL * self.width, gc(COLOR_BORDER))
			else:
				for row in range(1, self.height-1):
					self.win.addstr(row, self.width//2, VERTICAL_BORDER_SYMBOL, gc(COLOR_BORDER))

		if(self.active_editor_index < 1):
			self.win.addstr(self.height//2, 0, pad_center_str("No files selected", self.width), gc(COLOR_LIGHTGRAY_ON_DARKGRAY))
		else:
			self.editor1.repaint()
			if(self.editor2 != None): self.editor2.repaint()
			
		self.win.refresh()