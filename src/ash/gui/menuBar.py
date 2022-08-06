# ---------------------------------------------------------------------------------------------
#  Copyright (c) Akash Nag. All rights reserved.
#  Licensed under the MIT License. See LICENSE.md in the project root for license information.
# ---------------------------------------------------------------------------------------------

# This module implements the text-editor widget

from ash import *
from ash.gui import *
from ash.formatting.colors import *

class MenuBar:
	def __init__(self, parent, win, y, x, supports_colors):
		self.parent = parent
		self.y = y
		self.x = x
		self.win = win
		self.supports_colors = supports_colors
		self.items = list()
		self.item_offsets = list()
		self.active_menu_index = -1

	def add_menu(self, text, dropdown_menu):
		self.items.append( (text, dropdown_menu) )
		self.active_menu_index = 0
		self.update_item_offsets()
	
	def update_item_offsets(self):
		offset = self.x
		self.item_offsets = list()
		for text, _ in self.items:
			self.item_offsets.append( (offset + 1, offset + len(text) ))
			offset += len(text) + 2

	def get_menu_index_from_offset(self, y, x):
		if(y != self.y): return -1
		for i, (x1, x2) in enumerate(self.item_offsets):
			if(x >= x1 and x <= x2): return i
		return -1

	def perform_action(self, ch):
		if(self.active_menu_index < 0): return
		if(KeyBindings.is_key(ch, "LIST_MOVE_SELECTION_PREVIOUS")):
			self.parent.repaint()
			self.active_menu_index = (self.active_menu_index - 1) % len(self.items)
			self.show_dropdown()
		elif(KeyBindings.is_key(ch, "LIST_MOVE_SELECTION_NEXT")):
			self.parent.repaint()
			self.active_menu_index = (self.active_menu_index + 1) % len(self.items)
			self.show_dropdown()
		elif(KeyBindings.is_key(ch, "LIST_MOVE_SELECTION_DOWN")):
			self.show_dropdown()
		elif(KeyBindings.is_key(ch, "RESIZE_WINDOW")):
			self.parent.readjust()

	def mouse_click(self, btn, y, x):
		menu_index = self.get_menu_index_from_offset(y, x)
		if(menu_index > -1 and menu_index != self.active_menu_index):
			self.active_menu_index = menu_index
			self.show_dropdown()		
		
	def get_width(self):
		if(self.active_menu_index < 0): return 0
		text = self.items[self.active_menu_index][0]
		return 2 + len(text)

	def show_dropdown(self):
		if(self.active_menu_index < 0): return
		dropdown = self.items[self.active_menu_index][1]
		if(dropdown == None): return
		self.repaint(self.last_width, partial = True)
		self.win.refresh()
		dropdown.show()

	def repaint(self, width, partial = False):
		if(not partial):
			self.win.addstr(self.y, self.x, " " * width, gc("menu-bar") | (0 if self.supports_colors else curses.A_REVERSE))
		
		offset = self.x
		for i, menu in enumerate(self.items):
			text = menu[0]
			dropdown = menu[1]
			if(i == self.active_menu_index):
				self.win.addstr(self.y, offset, BORDER_VERTICAL + text + BORDER_VERTICAL, gc("menu-bar") | (0 if self.supports_colors else curses.A_REVERSE))
			else:
				self.win.addstr(self.y, offset, " " + text + " ", gc("menu-bar") | (0 if self.supports_colors else curses.A_REVERSE))
			offset += len(text)+2

		self.last_width = width