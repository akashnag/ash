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

class TopLevelWindow(Window):
	def __init__(self, stdscr, title, contrast_theme, handler_func):
		height, width = stdscr.getmaxyx()
		super().__init__(0, 0, height, width, title)
		self.status = None
		self.contrast_theme = contrast_theme
		self.win = stdscr
		self.handler_func = handler_func
				
	# adds a status bar
	def add_status_bar(self, status):
		self.status = status

	# returns the statusbar widget if any
	def get_status_bar(self):
		return self.status
			
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

			if(ch > -1 and self.active_widget_index > -1):
				self.get_active_widget().perform_action(ch)

			self.repaint()
			
	# check if terminal window has been resized, if so, readjust
	def readjust(self):
		self.height, self.width = self.win.getmaxyx()
		for w in self.widgets:
			w.readjust()

	# draws the window
	def repaint(self):
		if(self.win == None): return
		
		self.readjust()
		self.win.clear()
		self.win.addstr(0, 0, pad_center_str(self.title, self.width), curses.A_BOLD | self.contrast_theme)
		if(self.status != None): self.win.addstr(self.height-1, 0, str(self.status), self.contrast_theme)

		for w in self.widgets: 
			w.repaint()
			
		self.win.refresh()