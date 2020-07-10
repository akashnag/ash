# ---------------------------------------------------------------------------------------------
#  Copyright (c) Akash Nag. All rights reserved.
#  Licensed under the MIT License. See LICENSE.md in the project root for license information.
# ---------------------------------------------------------------------------------------------

# This module is a helper class for TopLevelWindow

from ash.gui import *
from ash.gui.editor import *

# note: layout values must begin at 0
LAYOUT_SINGLE 			= 0
LAYOUT_HORIZONTAL_2		= 1
LAYOUT_HORIZONTAL_3		= 2
LAYOUT_HORIZONTAL_4		= 3
LAYOUT_VERTICAL_2		= 4
LAYOUT_2X2				= 5
LAYOUT_2X3				= 6
LAYOUT_1L_2VR			= 7
LAYOUT_2VL_1R			= 8
LAYOUT_1T_2HB			= 9
LAYOUT_2HT_1B			= 10

# note: editor_count order must match the order of the layout values
EDITOR_COUNTS = [ 1, 2, 3, 4, 2, 4, 6, 3, 3, 3, 3 ]

APP_MODE_FILE		= 1		# if ash is invoked with zero or more file names
APP_MODE_PROJECT	= 2		# if ash is invoked with a single directory name

class LayoutManager:
	def __init__(self, win):
		self.win = win

	# draw the line divisions between editors
	def draw_layout_borders(self):
		half_width_right = self.win.width - (self.win.width // 2)

		if(self.win.layout_type == LAYOUT_SINGLE): 
			# a single pane (no borders)
			return		
		elif(self.win.layout_type == LAYOUT_VERTICAL_2):
			# two panes stacked on top of each other
			self.win.addstr(self.win.height // 2, 0, BORDER_HORIZONTAL * self.win.width, gc("inner-border"))
		elif(self.win.layout_type == LAYOUT_HORIZONTAL_2):
			# two panes side by side
			for row in range(1, self.win.height-1):
				self.win.addstr(row, self.win.width // 2, BORDER_VERTICAL, gc("inner-border"))
		elif(self.win.layout_type == LAYOUT_HORIZONTAL_3):
			# three panes side by side
			for row in range(1, self.win.height-1):
				self.win.addstr(row, self.win.width // 3, BORDER_VERTICAL, gc("inner-border"))
				self.win.addstr(row, (self.win.width * 2) // 3, BORDER_VERTICAL, gc("inner-border"))
		elif(self.win.layout_type == LAYOUT_HORIZONTAL_4):
			# four panes side by side
			for row in range(1, self.win.height-1):
				self.win.addstr(row, self.win.width // 4, BORDER_VERTICAL, gc("inner-border"))
				self.win.addstr(row, self.win.width // 2, BORDER_VERTICAL, gc("inner-border"))
				self.win.addstr(row, (self.win.width * 3) // 4, BORDER_VERTICAL, gc("inner-border"))
		elif(self.win.layout_type == LAYOUT_2X2):
			# four panes in a grid
			for row in range(1, self.win.height-1):
				self.win.addstr(row, self.win.width // 2, BORDER_VERTICAL, gc("inner-border"))
			self.win.addstr(self.win.height // 2, 0, BORDER_HORIZONTAL * self.win.width, gc("inner-border"))
			self.win.addstr(self.win.height // 2, self.win.width//2, BORDER_CROSSROADS, gc("inner-border"))
		elif(self.win.layout_type == LAYOUT_2X3):
			# three panes side by side above another three panes side by side
			self.win.addstr(self.win.height // 2, 0, BORDER_HORIZONTAL * self.win.width, gc("inner-border"))
			for row in range(1, self.win.height-1):
				self.win.addstr(row, self.win.width // 3, BORDER_VERTICAL, gc("inner-border"))
				self.win.addstr(row, (self.win.width * 2) // 3, BORDER_VERTICAL, gc("inner-border"))
			self.win.addstr(self.win.height // 2, self.win.width // 3, BORDER_CROSSROADS, gc("inner-border"))
			self.win.addstr(self.win.height // 2, (self.win.width * 2) // 3, BORDER_CROSSROADS, gc("inner-border"))
		elif(self.win.layout_type == LAYOUT_1L_2VR):
			# one pane to the left, two panes (stacked on top of each other) on the right
			for row in range(1, self.win.height-1):
				self.win.addstr(row, self.win.width // 2, BORDER_VERTICAL, gc("inner-border"))
			self.win.addstr(self.win.height // 2, self.win.width // 2, BORDER_HORIZONTAL * half_width_right, gc("inner-border"))
			self.win.addstr(self.win.height // 2, self.win.width // 2, BORDER_SPLIT_RIGHT, gc("inner-border"))
		elif(self.win.layout_type == LAYOUT_2VL_1R):
			# one pane to the right, two panes (stacked on top of each other) on the left
			for row in range(1, self.win.height-1):
				self.win.addstr(row, self.win.width // 2, BORDER_VERTICAL, gc("inner-border"))
			self.win.addstr(self.win.height // 2, 0, BORDER_HORIZONTAL * (self.win.width // 2), gc("inner-border"))
			self.win.addstr(self.win.height // 2, self.win.width // 2, BORDER_SPLIT_LEFT, gc("inner-border"))
		elif(self.win.layout_type == LAYOUT_1T_2HB):
			# one pane to the top spanning the entire width, two panes (side by side) on the bottom
			self.win.addstr(self.win.height // 2, 0, BORDER_HORIZONTAL * self.win.width, gc("inner-border"))
			for row in range(self.win.height // 2, self.win.height-1):
				self.win.addstr(row, self.win.width // 2, BORDER_VERTICAL, gc("inner-border"))
			self.win.addstr(self.win.height // 2, self.win.width // 2, BORDER_SPLIT_BOTTOM, gc("inner-border"))
		elif(self.win.layout_type == LAYOUT_2HT_1B):
			# one pane at the bottom spanning the entire width, two panes (side by side) on the top
			self.win.addstr(self.win.height // 2, 0, BORDER_HORIZONTAL * self.win.width, gc("inner-border"))
			for row in range(1, self.win.height // 2):
				self.win.addstr(row, self.win.width // 2, BORDER_VERTICAL, gc("inner-border"))
			self.win.addstr(self.win.height // 2, self.win.width // 2, BORDER_SPLIT_TOP, gc("inner-border"))
	

	# check if terminal window has been resized, if so, readjust
	def readjust(self, forced=False):
		h, w = self.win.app.readjust()
		if(not forced and h == self.win.height and w == self.win.width): return
		
		self.win.height, self.win.width = h, w

		ec = EDITOR_COUNTS[self.win.layout_type]
		dim = self.get_dimensions(self.win.layout_type)
		for i in range(ec):
			if(self.editor_exists(i)):
				y = dim[i].get("y")
				x = dim[i].get("x")
				h = dim[i].get("height")
				w = dim[i].get("width")
				self.win.editors[i].resize(y, x, h, w, True)
	
	# repaint editor if available or appropriate text
	def repaint_editors(self):
		ec = EDITOR_COUNTS[self.win.layout_type]
		dim = self.get_dimensions(self.win.layout_type)
		aed = self.win.get_active_editor()

		# Note: editor repaint must be done after self.__addstr() to correctly
		# reposition cursor inside the editor
		for i in range(ec):
			if(self.win.editors[i] == None):
				y, x, w = self.get_center_of_area(dim[i])
				self.__addstr(y, x, w)

		for i in range(ec):
			if(self.editor_exists(i) and i != self.win.active_editor_index):
				self.win.editors[i].repaint()
				
		if(aed != None): aed.repaint()
		
	# checks if given editor exists
	def editor_exists(self, index):
		if(index >= len(self.win.editors)): return False
		return (False if self.win.editors[index] == None else True)

	# returns the appropriate position of text to be placed in center-vertical position in the area
	def get_center_of_area(self, area):
		# Example:
		# y=1,h=8 = y-->(y+h-1) = 1-->8, center = 4.5 (4)
		# y=1,h=9 = y-->(y+h-1) = 1-->9, center = 5
		start_y = area.get("y")
		end_y = (area.get("y") + area.get("height") - 1)
		y = (start_y + end_y) // 2
		x = area.get("x")
		w = area.get("width")-1
		return (y, x, w)
		
	def __addstr(self, y, x, w):
		self.win.win.addstr(y, x, "No files selected".center(w), gc("disabled"))

	def get_dimensions(self, layout_type):
		if(self.win.layout_type == LAYOUT_SINGLE): 
			return([{
				"y": 1,
				"x": 0,
				"height": (self.win.height-2),
				"width": self.win.width
			}])
		elif(self.win.layout_type == LAYOUT_VERTICAL_2):
			# H=24: 1-11 |12| 13-22
			# H=23: 1-11 |12| 13-23
			return([{	#1
				"y": 1,
				"x": 0,
				"height": (self.win.height-2) // 2,
				"width": self.win.width
			}, {		#2
				"y": ((self.win.height-2) // 2) + 2,
				"x": 0,
				"height": ((self.win.height-2) // 2) - (1 - (self.win.height % 2)),
				"width": self.win.width
			}])
		elif(self.win.layout_type == LAYOUT_HORIZONTAL_2):
			# W=100: 0-49 |50| 51-99
			# W=101: 0-49 |50| 51-100
			return([{	#1
				"y": 1,
				"x": 0,
				"height": self.win.height-2,
				"width": (self.win.width // 2)
			}, {		#2
				"y": 1,
				"x": (self.win.width // 2) + 1,
				"height": self.win.height-2,
				"width": (self.win.width // 2) - (1 - (self.win.width % 2))
			}])
		elif(self.win.layout_type == LAYOUT_HORIZONTAL_3):
			# W=100: 0-32 |33| 34-65 |66| 67-99
			# W=101: 0-32 |33| 34-65 |66| 67-100
			return([{	#1
				"y": 1,
				"x": 0,
				"height": self.win.height-2,
				"width": (self.win.width // 3)
			}, {		#2
				"y": 1,
				"x": (self.win.width // 3) + 1,
				"height": self.win.height-2,
				"width": (self.win.width // 3) - 1
			}, {		#3
				"y": 1,
				"x": ((self.win.width * 2) // 3) + 1,
				"height": self.win.height-2,
				"width": (self.win.width // 3) + (self.win.width % 2)
			}])
		elif(self.win.layout_type == LAYOUT_HORIZONTAL_4):
			# 100: 0-24 |25| 26-49 |50| 51-74 |75| 76-99
			# 101: 0-24 |25| 26-49 |50| 51-74 |75| 76-100
			return([{	#1
				"y": 1,
				"x": 0,
				"height": self.win.height-2,
				"width": (self.win.width // 4)
			}, {		#2
				"y": 1,
				"x": (self.win.width // 4) + 1,
				"height": self.win.height-2,
				"width": (self.win.width // 4) - 1
			}, {		#3
				"y": 1,
				"x": (self.win.width // 2) + 1,
				"height": self.win.height-2,
				"width": (self.win.width // 4) - 1
			}, {		#4
				"y": 1,
				"x": ((self.win.width * 3) // 4) + 1,
				"height": self.win.height-2,
				"width": (self.win.width // 4) - (1 - (self.win.width % 2))
			}])
		elif(self.win.layout_type == LAYOUT_2X2):
			# width=100: x: 0-49 |50| 51-99; height=24: y: 1-11 |12| 13-22
			# width=101: x: 0-49 |50| 51-100; height=25: y: 1-11 |12| 13-23
			return([{	#1
				"y": 1,
				"x": 0,
				"height": (self.win.height-2) // 2,
				"width": (self.win.width // 2)
			}, {		#2
				"y": 1,
				"x": (self.win.width // 2) + 1,
				"height": (self.win.height-2) // 2,
				"width": (self.win.width // 2) - (1 - (self.win.width % 2))
			}, {		#3
				"y": (self.win.height // 2) + 1,
				"x": 0,
				"height": ((self.win.height-2) // 2) - (1 - (self.win.height % 2)),
				"width": (self.win.width // 2)
			}, {		#4
				"y": (self.win.height // 2) + 1,
				"x": (self.win.width // 2) + 1,
				"height": ((self.win.height-2) // 2) - (1 - (self.win.height % 2)),
				"width": (self.win.width // 2) - (1 - (self.win.width % 2))
			}])
		elif(self.win.layout_type == LAYOUT_2X3):
			# width=100: x: 0-32 |33| 34-65 |66| 67-99 ; height=24: y: 1-11 |12| 13-22
			# width=101: x: 0-32 |33| 34-65 |66| 67-100; height=25: y: 1-11 |12| 13-23
			return([{	#1
				"y": 1,
				"x": 0,
				"height": (self.win.height-2) // 2,
				"width": (self.win.width // 3)
			}, {		#2
				"y": 1,
				"x": (self.win.width // 3) + 1,
				"height": (self.win.height-2) // 2,
				"width": (self.win.width // 3) - 1
			}, {		#3
				"y": 1,
				"x": ((self.win.width * 2) // 3) + 1,
				"height": (self.win.height-2) // 2,
				"width": (self.win.width // 3) + (self.win.width % 2)
			}, {		#4
				"y": (self.win.height // 2) + 1,
				"x": 0,
				"height": ((self.win.height-2) // 2) - (1 - (self.win.height % 2)),
				"width": (self.win.width // 3)
			}, {		#5
				"y": (self.win.height // 2) + 1,
				"x": (self.win.width // 3) + 1,
				"height": ((self.win.height-2) // 2) - (1 - (self.win.height % 2)),
				"width": (self.win.width // 3) - 1
			}, {		#6
				"y": (self.win.height // 2) + 1,
				"x": ((self.win.width * 2) // 3) + 1,
				"height": ((self.win.height-2) // 2) - (1 - (self.win.height % 2)),
				"width": (self.win.width // 3) + (self.win.width % 2)
			}])
		elif(self.win.layout_type == LAYOUT_1L_2VR):
			# width=100: x: 0-49 |50| 51-99 ; height=24: y: (1-22) & (1-11 |12| 13-22)
			# width=101: x: 0-49 |50| 51-100; height=25: y: (1-23) & (1-11 |12| 13-23)
			return([{	#1
				"y": 1,
				"x": 0,
				"height": (self.win.height-2),
				"width": (self.win.width // 2)
			}, {		#2
				"y": 1,
				"x": (self.win.width // 2) + 1,
				"height": (self.win.height-2) // 2,
				"width": (self.win.width // 2) - (1 - (self.win.width % 2))
			}, {		#3
				"y": (self.win.height // 2) + 1,
				"x": (self.win.width // 2) + 1,
				"height": (self.win.height-2) // 2 - (1 - (self.win.height % 2)),
				"width": (self.win.width // 2) - (1 - (self.win.width % 2))
			}])
		elif(self.win.layout_type == LAYOUT_2VL_1R):
			# width=100: x: 0-49 |50| 51-99 ; height=24: y: (1-11 |12| 13-22) & (1-22)
			# width=101: x: 0-49 |50| 51-100; height=25: y: (1-11 |12| 13-23) & (1-23)
			return([{	#1
				"y": 1,
				"x": 0,
				"height": (self.win.height-2) // 2,
				"width": (self.win.width // 2)
			}, {		#2
				"y": (self.win.height // 2) + 1,
				"x": 0,
				"height": ((self.win.height-2) // 2) - (1 - (self.win.height % 2)),
				"width": (self.win.width // 2)
			}, {		#3
				"y": 1,
				"x": (self.win.width // 2) + 1,
				"height": (self.win.height-2),
				"width": (self.win.width // 2) - (1 - (self.win.width % 2))
			}])
		elif(self.win.layout_type == LAYOUT_1T_2HB):
			# width=100: x: (0-99) & (0-49 |50| 51-99) ; height=24: y: 1-11 |12| 13-22
			# width=101: x: (0-100) & (0-49 |50| 51-100); height=25: y: 1-11 |12| 13-23
			return([{	#1
				"y": 1,
				"x": 0,
				"height": (self.win.height-2) // 2,
				"width": self.win.width
			}, {		#2
				"y": (self.win.height // 2) + 1,
				"x": 0,
				"height": ((self.win.height-2) // 2) - (1 - (self.win.height % 2)),
				"width": (self.win.width // 2)
			}, {		#3
				"y": (self.win.height // 2) + 1,
				"x": (self.win.width // 2) + 1,
				"height": ((self.win.height-2) // 2) - (1 - (self.win.height % 2)),
				"width": (self.win.width // 2) - (1 - (self.win.width % 2))
			}])
		elif(self.win.layout_type == LAYOUT_2HT_1B):
			# width=100: x: (0-49 |50| 51-99) & (0-99) ; height=24: y: 1-11 |12| 13-22
			# width=101: x: (0-49 |50| 51-100) & (0-100); height=25: y: 1-11 |12| 13-23
			return([{	#1
				"y": 1,
				"x": 0,
				"height": (self.win.height-2) // 2,
				"width": (self.win.width // 2)
			}, {		#2
				"y": 1,
				"x": (self.win.width // 2) + 1,
				"height": (self.win.height-2) // 2,
				"width": (self.win.width // 2) - (1 - (self.win.width % 2))
			}, {		#3
				"y": (self.win.height // 2) + 1,
				"x": 0,
				"height": ((self.win.height-2) // 2) - (1 - (self.win.height % 2)),
				"width": self.win.width
			}])

	# changes the current layout: add code to attach/detach editors
	def set_layout(self, layout_type):
		old_ec = EDITOR_COUNTS[self.win.layout_type]
		new_ec = EDITOR_COUNTS[layout_type]

		if(new_ec >= old_ec):						# increase the no. of editors
			for i in range(old_ec, new_ec):
				self.win.editors.append(None)
		else:										# decrease the no. of editors
			for i in range(new_ec, old_ec):
				self.win.editors[new_ec].destroy()
				self.win.editors.pop(new_ec)

		self.win.layout_type = layout_type			
		self.readjust(True)
		self.win.repaint()

	# called from app_main() in response to Function key press
	def invoke_activate_editor(self, index, new_bid = None, new_buffer = None):
		ec = EDITOR_COUNTS[self.win.layout_type]
		aei = self.win.active_editor_index
		
		# layout does not support that editor
		if(index >= ec):
			self.win.app.show_error("Selected editor does not exist")
			return None
				
		# if already active, return		
		if(aei == index):
			if(new_bid != None and new_buffer != None): 
				self.win.editors[index].set_buffer(new_bid, new_buffer)
			return
				
		if(self.win.editors[index] == None):
			if(new_bid != None and new_buffer != None):
				self.win.editors[index] = Editor(self.win)
				self.win.editors[index].set_buffer(new_bid, new_buffer)
			else:
				if(self.win.app.app_mode == APP_MODE_FILE):
					if(self.win.app.ask_question("SELECT FILE", "Select YES to open a blank-buffer, or NO to open a file")):
						new_bid, new_buffer = self.win.app.buffers.create_new_buffer()
						self.win.editors[index] = Editor(self.win)
						self.win.editors[index].set_buffer(new_bid, new_buffer)
					else:
						self.win.app.dialog_handler.invoke_file_open(index)						
				else:
					self.win.app.dialog_handler.invoke_project_explorer(index)				
				if(self.win.editors[index] == None or self.win.editors[index].buffer == None): return

		# set active editor
		self.win.active_editor_index = index

		self.readjust(True)
		self.win.repaint()
		
		if(aei >= 0): self.win.editors[aei].blur()
		self.win.editors[index].focus()
		
		return self.win.editors[index]