# ---------------------------------------------------------------------------------------------
#  Copyright (c) Akash Nag. All rights reserved.
#  Licensed under the MIT License. See LICENSE.md in the project root for license information.
# ---------------------------------------------------------------------------------------------

# This module implements the ListBox widget

from ash.widgets import *

class ListBox(Widget):
	def __init__(self, parent, y, x, width, row_count, items, theme, focus_theme):
		super(ListBox, self).__init__(WIDGET_TYPE_LISTBOX)
		self.parent = parent
		self.y = y
		self.x = x
		self.width = width
		self.row_count = row_count
		self.items = items
		self.theme = theme
		self.focus_theme = focus_theme
		self.sel_index = -1
		self.is_in_focus = False
		self.repaint()

	# when focus received
	def focus(self):
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

	# draw the listbox
	def repaint(self):
		if(self.is_in_focus): curses.curs_set(False)
		
		count = len(self.items)
		if(count <= self.row_count):
			start = 0
			end = count
		elif(self.sel_index == -1):
			start = 0
			end = self.row_count
		else:
			flank = self.row_count // 2
			start = self.sel_index - flank
			end = self.sel_index + flank

			if(start < 0):
				delta = abs(start)
				start += delta
				end += delta				
			elif(end > count):
				delta = end - count
				start -= delta
				end -= delta
			elif(start == end and end < count):
				end += 1

		for i in range(start, end):
			n = 2 + len(str(self.items[i]))
			if(n > self.width):
				text = " " + str(self.items[i])[0:self.width-2] + " "
			else:
				text = " " + str(self.items[i]) + (" " * (self.width-n+1))

			if(i == self.sel_index):
				if(self.is_in_focus):
					self.parent.addstr(self.y + i - start, self.x, text, self.focus_theme)
				else:
					self.parent.addstr(self.y + i - start, self.x, text, curses.A_REVERSE | self.theme)
			else:				
				self.parent.addstr(self.y + i - start, self.x, text, self.theme)
	
	# handle key presses
	def perform_action(self, ch):
		self.focus()
		n = len(self.items)
		if(n == 0):
			self.sel_index = -1
			beep()
		elif(ch == curses.KEY_UP):
			if(self.sel_index == -1):
				self.sel_index = n-1
			else:
				self.sel_index = (self.sel_index - 1) % n
		elif(ch == curses.KEY_DOWN):
			self.sel_index = (self.sel_index + 1) % n
		else:
			beep()
		self.repaint()

	# append an item to the list
	def add_item(self, item):
		self.items.append(item)

	# remove an item from the list
	def remove_item(self, index):
		self.items.pop(index)
		if(self.sel_index == index): self.sel_index = -1

	# insert an item in the middle of the list
	def insert_item(self, index, item):
		self.items.insert(index, item)
		if(self.sel_index == index): self.sel_index += 1

	# returns the text of the selected item
	def __str__(self):
		return self.get_sel_text()