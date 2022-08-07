# ---------------------------------------------------------------------------------------------
#  Copyright (c) Akash Nag. All rights reserved.
#  Licensed under the MIT License. See LICENSE.md in the project root for license information.
# ---------------------------------------------------------------------------------------------

# This module implements the text-editor widget

from ash import *
from ash.gui import *
from ash.formatting.colors import *

class PopupMenu:
	def __init__(self, parent, y, x, menu_items, width=20, is_dropdown=False, parent_menu=None, supports_colors=True):
		self.parent = parent
		self.y = y
		self.x = x
		self.items = menu_items
		self.height = len(self.items) + 2
		self.width = width
		self.win = None
		self.sel_index = 0
		self.is_dropdown = is_dropdown
		self.parent_menu = parent_menu
		self.supports_colors = supports_colors

	def get_menu_index_from_offset(self, y, x):
		item_index = y - self.y - 1
		if(item_index >= len(self.items)): return -1
		if(x <= self.x + 1 or x >= self.x + self.width - 1): return -1
		return item_index

	def select_item(self, index):
		func = self.items[index][2]
		if(func == None): return False
		if(type(func) == tuple):
			func_name = func[0]
			params = func[1]
		else:
			func_name = func
			params = None

		self.win = None
		self.parent.repaint()
		if(params == None):
			ret_code = func_name()
		else:
			ret_code = func_name(params)
		
		# hide the menu bar
		self.win = None
		obj = self
		while(obj != None):
			try:
				obj.parent.hide_menu_bar()
				break
			except:
				obj = obj.parent_menu
				
		if(type(ret_code) != bool):
			return False
		else:
			return ret_code

	def hide_menu_bar(self):
		self.win = None
		obj = self
		while(obj != None):
			try:
				obj.parent.hide_menu_bar()
				break
			except:
				obj = obj.parent_menu

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
				return self.select_item(self.sel_index)
			elif(KeyBindings.is_key(ch, "CLOSE_WINDOW") or KeyBindings.is_key(ch, "RIGHT_CLICK")):
				self.win = None
			elif(self.is_dropdown and (KeyBindings.is_key(ch, "LIST_MOVE_SELECTION_NEXT") or KeyBindings.is_key(ch, "LIST_MOVE_SELECTION_PREVIOUS"))):
				self.win = None
				self.parent_menu.perform_action(ch)
			elif(self.is_dropdown and KeyBindings.is_key(ch, "HIDE_MENU_BAR")):
				self.hide_menu_bar()
			elif(KeyBindings.is_key(ch, "RESIZE_WINDOW")):
				self.win = None
				self.parent_menu.perform_action(ch)
			elif(KeyBindings.is_mouse(ch)):
				btn, y, x = KeyBindings.get_mouse(ch)
				menu_index = self.get_menu_index_from_offset(y, x)
				if(btn == MOUSE_CLICK and menu_index > -1):
					self.sel_index = menu_index
					self.repaint()
					time.sleep(0.1)
					self.select_item(self.sel_index)
				elif(btn == MOUSE_CLICK and self.parent_menu != None):
					self.hide_menu_bar()
					self.parent_menu.repaint(self.parent_menu.parent.width)
					self.parent_menu.mouse_click(btn, y, x)
				elif(btn != None):
					self.win = None					

			self.repaint()

		return False			# True if edit made

	def repaint(self):
		if(self.win == None): return

		style_name = ("dropdown" if self.is_dropdown else "popup")

		self.win.clear()
		self.win.attron(gc(style_name + "-border") | (0 if self.supports_colors else curses.A_REVERSE))
		self.win.border()
		self.win.attroff(gc(style_name + "-border") | (0 if self.supports_colors else curses.A_REVERSE))

		# if part of top-level menu-bar, then make opening for menu
		if(self.is_dropdown and self.parent_menu.get_width() > 0):
			self.win.addstr(0, 0, BORDER_VERTICAL, gc(style_name + "-border") | (0 if self.supports_colors else curses.A_REVERSE))
			self.win.addstr(0, 1, " " * (self.parent_menu.get_width()-2), gc(style_name + "-border") | (0 if self.supports_colors else curses.A_REVERSE))
			self.win.addstr(0, self.parent_menu.get_width() - 1, BORDER_BOTTOM_LEFT, gc(style_name + "-border") | (0 if self.supports_colors else curses.A_REVERSE))

		curses.curs_set(False)
		for y in range(self.height-2):
			text, enabled, _ = self.items[y]
			
			if(text == "---"):
				self.win.addstr(y + 1, 0, BORDER_SPLIT_RIGHT, gc(style_name + "-border") | (0 if self.supports_colors else curses.A_REVERSE))
				self.win.addstr(y + 1, self.width-1, BORDER_SPLIT_LEFT,  gc(style_name + "-border") | (0 if self.supports_colors else curses.A_REVERSE))
				self.win.addstr(y + 1, 1, BORDER_HORIZONTAL * (self.width-2),  gc(style_name + "-border") | (0 if self.supports_colors else curses.A_REVERSE))
			elif(y == self.sel_index):
				if(enabled):
					style = gc(style_name + "-selection")
				else:
					style = gc(style_name + "-disabled-selection")
				self.win.addstr(y + 1, 1, (" " + text).ljust(self.width-2), style)
			else:
				if(not enabled): 
					style = gc(style_name + "-disabled") | (0 if self.supports_colors else curses.A_REVERSE)
				else:
					style = gc(style_name) | (0 if self.supports_colors else curses.A_REVERSE)
				self.win.addstr(y + 1, 1, (" " + text).ljust(self.width-2), style)

		self.win.refresh()

	def get_bounds(self):
		return(self.y, self.x, self.height, self.width)

	def get_relative_coords(self, y, x):
		return(y - self.y, x - self.x)