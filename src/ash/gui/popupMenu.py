# ---------------------------------------------------------------------------------------------
#  Copyright (c) Akash Nag. All rights reserved.
#  Licensed under the MIT License. See LICENSE.md in the project root for license information.
# ---------------------------------------------------------------------------------------------

# This module implements the text-editor widget

from ash import *
from ash.gui import *
from ash.formatting.colors import *

class PopupMenu:
	def __init__(self, parent, y, x, menu_items):
		self.parent = parent
		self.y = y
		self.x = x
		self.items = menu_items
		self.height = len(self.items) + 2
		self.width = 20							# make it variable
		self.win = None
		self.sel_index = 0

	def show(self):
		self.win = curses.newwin(self.height, self.width, self.y, self.x)
		
		curses.curs_set(False)
		self.win.keypad(True)
		self.win.timeout(0)
		self.repaint()

		while(self.win != None):
			ch = self.win.getch()
			if(ch == -1): continue
			
			if(KeyBindings.is_key(ch, "LIST_MOVE_SELECTION_UP")):
				while(True):
					self.sel_index = (self.sel_index - 1) % len(self.items)
					if(self.items[self.sel_index][0] != "---"): break
			elif(KeyBindings.is_key(ch, "LIST_MOVE_SELECTION_DOWN")):
				while(True):
					self.sel_index = (self.sel_index + 1) % len(self.items)
					if(self.items[self.sel_index][0] != "---"): break
			elif(KeyBindings.is_key(ch, "LIST_MAKE_SELECTION")):
				func = self.items[self.sel_index][2]
				self.win = None
				ret_code = func()
				if(type(ret_code) != bool):
					return False
				else:
					return ret_code
			elif(KeyBindings.is_key(ch, "CLOSE_WINDOW") or KeyBindings.is_keyboard_right_click(ch)):
				self.win = None
			elif(KeyBindings.is_mouse(ch)):
				pass

			self.repaint()

		return False			# True if edit made

	def repaint(self):
		if(self.win == None): return

		self.win.clear()
		self.win.attron(gc("popup-border"))
		self.win.border()
		self.win.attroff(gc("popup-border"))

		curses.curs_set(False)
		for y in range(self.height-2):
			text, enabled, _ = self.items[y]
			style = gc("popup")
			if(text == "---"):
				self.win.addstr(y + 1, 0, BORDER_SPLIT_RIGHT, gc("popup-border"))
				self.win.addstr(y + 1, self.width-1, BORDER_SPLIT_LEFT,  gc("popup-border"))
				self.win.addstr(y + 1, 1, BORDER_HORIZONTAL * (self.width-2),  gc("popup-border"))
			elif(y == self.sel_index):
				if(enabled):
					style = gc("popup-selection")
				else:
					style = gc("popup-disabled-selection")
				self.win.addstr(y + 1, 1, (" " + text).ljust(self.width-2), style)
			else:
				if(not enabled): style = gc("popup-disabled")
				self.win.addstr(y + 1, 1, (" " + text).ljust(self.width-2), style)

		self.win.refresh()

	def get_bounds(self):
		return(self.y, self.x, self.height, self.width)

	def get_relative_coords(self, y, x):
		return(y - self.y, x - self.x)