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
from ash.widgets.layoutManager import *

# <-------------------- class declaration --------------->
class TopLevelWindow(Window):
	def __init__(self, app, stdscr, title, handler_func):
		super().__init__(0, 0, 0, 0, title)
		self.layout_manager = LayoutManager(self)
		self.app = app
		self.win = stdscr
		self.handler_func = handler_func
		self.editors = list()
		self.active_editor_index = -1
		self.layout_type = LAYOUT_SINGLE
			
	# adds an editor to the workspace
	def add_editor(self, ed):
		if(len(self.editors) == 6): return
		self.editors.append(ed)
		if(self.active_editor_index < 0 and ed != None): self.active_editor_index = 0

	# removes an editor from the workspace
	def remove_editor(self, index):
		self.editors.pop(index)
		if(self.active_editor_index == index):
			if(len(self.editors) == 0):
				self.active_editor_index = -1
			elif(index == 0):
				self.active_editor_index = 1
			else:
				self.active_editor_index -= 1

	# load data for an editor
	def set_editor_data(self, index, data):
		if(index < len(self.editors)):
			self.editors[index].set_data(data)

	# checks if layout can be changed
	def can_change_layout(self, layout_type):
		return self.layout_manager.can_change_layout(layout_type)
	
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
		if(self.active_editor_index >= 0):
			self.editors[self.active_editor_index] = None
			self.repaint()

	# closes a given editor
	def close_editor(self, index):
		self.editors[index] = None
		if(index == self.active_editor_index): self.active_editor_index = -1
		self.repaint()

	def update_status(self):
		aed = self.get_active_editor()

		language = ""
		editor_state = "inactive"
		cursor_position = ""
		loc_count = ""
		file_size = ""

		if(aed != None):
			lines, sloc = aed.get_loc()
			loc_count = str(lines) + " lines (" + str(sloc) + " sloc)"
			
			if(aed.has_been_allotted_file):
				if(os.path.isfile(aed.filename)): file_size = aed.get_file_size()
				language = get_file_type(aed.filename)
				if(language == None): language = "unknown"
				if(aed.save_status):
					editor_state = "saved"
				else:
					editor_state = "modified"
			else:
				editor_state = "unsaved"
				language = "unknown"

			cursor_position = str(aed.get_cursor_position())
		
		self.status.set(0, editor_state)
		self.status.set(1, language)
		self.status.set(2, loc_count)
		self.status.set(3, file_size)
		self.status.set(4, cursor_position)

		if(aed != None):
			self.set_title(self.app.get_app_title(aed))
		else:
			self.set_title(self.app.get_app_title())
	
	# shows the window and starts the event-loop
	def show(self):
		curses.curs_set(False)
		self.win.keypad(True)
		self.win.timeout(0)
		self.repaint()

		if(len(self.editors) > 0): self.editors[0].focus()

		while(True):
			ch = self.win.getch()
			if(ch == -1): continue
			
			# send Ctrl/Fn keypresses to main handler first
			if(self.handler_func != None and is_ctrl_or_func(ch)):
				ch = self.handler_func(ch)
				if(self.win == None): return

			if(ch == -1): continue
			
			if(self.active_editor_index > -1):
				self.get_active_editor().perform_action(ch)

			self.repaint()
			
	
	# draws the window
	def repaint(self):
		if(self.win == None): return
		
		self.update_status()
		self.layout_manager.readjust()
		self.win.clear()

		self.win.addstr(0, 0, pad_center_str(self.title, self.width), curses.A_BOLD | gc(COLOR_TITLEBAR))
		if(self.status != None): self.win.addstr(self.height-1, 0, str(self.status), gc(COLOR_STATUSBAR))

		self.layout_manager.draw_layout_borders()
		self.layout_manager.repaint_editors()
		
		self.win.refresh()

	# <----------------------------------- dialog boxes ----------------------------------->
	def reload_in_all(self, filename):
		aed = self.get_active_editor()
		if(aed == None): return			# not possible, since this fn was called from the active-editor on Ctrl+S

		reload_required = False
		n = len(self.editors)
		aei = self.active_editor_index

		# check if reload is necessary
		for i in range(n):
			if(i == aei): continue
			if(not self.layout_manager.editor_exists(i)): continue

			ed = self.editors[i]
			if(ed.has_been_allotted_file and ed.filename == filename):
				reload_required = True
				break

		if(not reload_required): return
		if(not self.app.ask_question("RELOAD", "Reload files in other editors?")): return

		for i in range(n):
			if(i == aei): continue
			if(not self.layout_manager.editor_exists(i)): continue

			ed = self.editors[i]
			if(ed.has_been_allotted_file and ed.filename == filename):
				ed.read_from_file()
				ed.save_status = True
				ed.repaint()

	
	def do_save_as(self, filename):
		aed = self.get_active_editor()
		if(aed == None): return
		
		# check if the filename is already in the active/recent files list
		fe = file_exists_in_buffer(self.app.files, filename)
		
		# write to file
		aed.allot_and_save_file(filename)

		# if not, add it to the workspace
		if(not fe):
			file_data = aed.get_data()
			self.app.files.append(file_data)