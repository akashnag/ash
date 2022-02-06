# ---------------------------------------------------------------------------------------------
#  Copyright (c) Akash Nag. All rights reserved.
#  Licensed under the MIT License. See LICENSE.md in the project root for license information.
# ---------------------------------------------------------------------------------------------

# This module implements the ListBox widget

from ash.gui import *

class ListBox(Widget):
	def __init__(self, parent, y, x, width, row_count, placeholder_text = None, callback = None, supports_colors=True):
		super(ListBox, self).__init__(WIDGET_TYPE_LISTBOX)
		self.parent = parent
		self.y = y
		self.x = x
		self.width = width
		self.height = row_count
		self.row_count = row_count
		self.placeholder_text = placeholder_text
		self.callback = callback
		self.supports_colors = supports_colors
		self.items = list()
		self.tags = list()
		self.should_highlight = list()
		self.theme = gc("global-default")
		self.focus_theme = gc("formfield-focussed")
		self.sel_blur_theme = gc("formfield-selection-blurred")
		self.sel_index = -1
		self.is_in_focus = False
		self.focussable = False
		self.list_start = 0
		self.list_end = 0
		self.repaint()

	# when focus received
	def focus(self):
		if(not self.focussable): return
		self.is_in_focus = True
		self.repaint()

	# when focus lost
	def blur(self):
		self.is_in_focus = False
		self.repaint()

	# returns the index of the selected item
	def get_sel_index(self):
		return self.sel_index

	# returns the text of the selected item
	def get_sel_text(self):
		if(self.sel_index < 0):
			return None
		else:
			return self.items[self.sel_index]

	# returns the tag of the selected item
	def get_sel_tag(self):
		if(self.sel_index < 0):
			return None
		else:
			return self.tags[self.sel_index]

	# draw the listbox
	def repaint(self):
		if(self.is_in_focus): curses.curs_set(False)
		
		count = len(self.items)
		if(self.sel_index == -1):
			self.list_start = 0
			self.list_end = min([self.row_count, count])
		elif(self.sel_index < self.list_start):
			self.list_start = self.sel_index
			self.list_end = min([self.list_start + self.row_count, count])
		elif(self.sel_index >= self.list_end):
			self.list_end = min([count, self.sel_index + 1])
			self.list_start = max([0, self.sel_index - self.row_count + 1])
			
		for i in range(self.list_start, self.list_end):
			n = 2 + len(str(self.items[i]))
			if(n > self.width):
				text = " " + str(self.items[i])[0:self.width-2] + " "
			else:
				text = " " + str(self.items[i]) + (" " * (self.width-n+1))
			
			if(i == self.sel_index):
				if(self.is_in_focus):
					style = self.focus_theme | (0 if self.supports_colors else curses.A_REVERSE)
					if(self.should_highlight[i]): style |= curses.A_BOLD
					self.parent.addstr(self.y + i - self.list_start, self.x, text, style)
				else:
					style = self.sel_blur_theme | (0 if self.supports_colors else curses.A_BOLD)
					if(self.should_highlight[i]): style |= curses.A_BOLD
					self.parent.addstr(self.y + i - self.list_start, self.x, text, style)
			else:
				style = self.theme
				if(self.should_highlight[i]): style = curses.A_BOLD | gc("global-highlighted")
				self.parent.addstr(self.y + i - self.list_start, self.x, text, style)

		if(count == 0): self.parent.addstr(self.y + (self.row_count // 2), self.x, ("" if self.placeholder_text == None else self.placeholder_text).center(self.width), gc("disabled"))
	
	# handle key presses
	def perform_action(self, ch):
		self.focus()
		n = len(self.items)

		if(n == 0):
			self.sel_index = -1
			beep()
		elif(KeyBindings.is_key(ch, "LIST_MOVE_SELECTION_UP")):
			if(self.sel_index <= 0):
				self.sel_index = 0
			else:
				self.sel_index = (self.sel_index - 1) % n
		elif(KeyBindings.is_key(ch, "LIST_MOVE_SELECTION_DOWN")):
			if(self.sel_index < n-1):
				self.sel_index = (self.sel_index + 1) % n
		elif(KeyBindings.is_key(ch, "LIST_MOVE_TO_PREVIOUS_PAGE")):
			if(self.sel_index > self.row_count):
				self.sel_index -= self.row_count
			else:
				self.sel_index = 0
		elif(KeyBindings.is_key(ch, "LIST_MOVE_TO_NEXT_PAGE")):
			if(self.sel_index < len(self.items) - self.row_count):
				self.sel_index += min([self.row_count, len(self.items)-1])
			else:
				self.sel_index = len(self.items)-1
		else:
			beep()

		if(self.callback != None): self.callback(self.sel_index)
		self.repaint()

	# append an item to the list
	def add_item(self, item, tag=None, highlight=False):
		self.items.append(item)
		self.tags.append(tag)
		self.should_highlight.append(highlight)
		if(self.sel_index < 0): self.sel_index = 0
		self.focussable = True
		self.list_start = 0
		self.list_end = min([self.row_count, len(self.items)])

	# remove an item from the list
	def remove_item(self, index):
		self.items.pop(index)
		self.tags.pop(index)
		if(len(self.items) == 0):
			self.sel_index = -1
			self.focussable = False
		else:
			self.sel_index = 0
		self.list_start = 0
		self.list_end = min([self.row_count, len(self.items)])

	# insert an item in the middle of the list
	def insert_item(self, index, item, tag=None):
		self.items.insert(index, item)
		self.tags.insert(index, tag)
		if(self.sel_index == index): self.sel_index += 1
		self.list_start = 0
		self.list_end = min([self.row_count, len(self.items)])

	# returns the text of the selected item
	def __str__(self):
		return self.get_sel_text()

	def clear(self):
		self.tags = list()
		self.items = list()
		self.should_highlight = list()
		self.sel_index = -1
		self.list_start = 0
		self.list_end = 0

	def on_click(self, y, x):
		if(len(self.items) > y + self.list_start):
			self.sel_index = y + self.list_start
			self.repaint()