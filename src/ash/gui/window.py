# ---------------------------------------------------------------------------------------------
#  Copyright (c) Akash Nag. All rights reserved.
#  Licensed under the MIT License. See LICENSE.md in the project root for license information.
# ---------------------------------------------------------------------------------------------

# This module implements:
# The abstract Window class from which Dialog and TopLevelWindow are derived

from ash.gui import *

class Window:
	def __init__(self, y, x, height, width, title):
		self.y = y
		self.x = x
		self.height = height
		self.width = width
		self.widgets = []
		self.widget_map = dict()
		self.active_widget_index = -1
		self.title = (title if len(title) <= self.width-2 else title[0:self.width-2])
	
	# returns the width of the window
	def get_width(self):
		return self.width

	# returns the height of the window
	def get_height(self):
		return self.height

	# sets the window title-bar text
	def set_title(self, title):
		self.title = title
	
	# stub for repaint(), to be overridden() by child
	def repaint(self):
		pass

	# stub for show(), to be overridden by child
	def show(self):
		pass

	# hides the window by destroying the underlying curses-window object
	def hide(self):
		self.win = None

	# interface to curses-window.addstr()
	def addstr(self, y, x, s, theme):
		try:
			if(self.win != None): self.win.addstr(y, x, s, theme)
		except:
			pass
			#self.win.addstr(0, 0, "ERROR: " + str(self.get_height()) + ", " + str(self.get_width()) + ", " + str(y) + ", " + str(x) + ", " + str(len(s)), gc("titlebar"))

	# interface to curses-window.move()
	def move(self, newy, newx):
		if(self.win != None): self.win.move(newy, newx)

	# returns the active widget
	def get_active_widget(self):
		if(self.active_widget_index < 0):
			return None
		else:
			return self.widgets[self.active_widget_index]

	# removes all widgets
	def remove_all_widgets(self):
		self.widgets = []
		self.widget_map = dict()
		self.active_widget_index = -1

	# returns the widget by name
	def get_widget(self, widget_name):
		index = self.widget_map.get(widget_name)
		if(index == None): return None
		return self.widgets[index]

	# adds a new widget to the window
	def add_widget(self, widget_name, widget):
		self.widgets.append(widget)
		self.widget_map[widget_name] = len(self.widgets) - 1

		if(self.active_widget_index == -1): 
			self.active_widget_index = self.get_next_focussable_widget_index()
			if(self.active_widget_index > -1):
				self.widgets[self.active_widget_index].focus()
	
	# returns the previous focussable widget in tab-order
	def get_previous_focussable_widget_index(self):
		count = len(self.widgets)
		if(count == 0): return -1

		if(self.active_widget_index == -1):
			start_index = count - 1
		else:
			start_index = (self.active_widget_index - 1) % count
		
		index = start_index

		while(True):
			if(self.widgets[index].is_focussable()):
				return index
			else:
				index = (index - 1) % count
				if(index == start_index): return -1

	# returns the next focussable widget in tab-order
	def get_next_focussable_widget_index(self):
		count = len(self.widgets)
		if(count == 0): return -1

		start_index = (self.active_widget_index + 1) % count
		index = start_index

		while(True):
			if(self.widgets[index].is_focussable()):
				return index
			else:
				index = (index + 1) % count
				if(index == start_index): return -1