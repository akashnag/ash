# ---------------------------------------------------------------------------------------------
#  Copyright (c) Akash Nag. All rights reserved.
#  Licensed under the MIT License. See LICENSE.md in the project root for license information.
# ---------------------------------------------------------------------------------------------

# This module implements:
# The WindowManager class which handles multiple tabs and editor configuration

from ash.gui import *
from ash.gui.editor import *
from ash.gui.statusbar import *
from ash.core.bufferManager import *

class TabNodeType:
	EDITOR 				= 0
	HORIZONTAL_SPLIT 	= 1
	VERTICAL_SPLIT 		= 2

class WindowArea:
	def __init__(self, y, x, height, width):
		self.y = y
		self.x = x
		self.height = height
		self.width = width

	def split_horizontally(self):
		y1 = self.y
		x1 = self.x
		h1 = self.height
		w1 = self.width // 2
		# width=100: 0,0,25,100: 0,0,25,50 & |x=50| & 0,51,25,49
		# width=50: 0,1,25,50: 0,1,25,25 & |x=26| & 0,27,25,24
		# width=50: 0,50,25,50: 0,50,25,25 & |x=75| & 0,76,25,24
		# width=51: 0,50,25,51: 0,50,25,25 & |x=75| & 0,76,25,25
		# width=101: 0,0,25,101: 0,0,25,50 & |x=50| & 0,51,25,50
		y2 = self.y
		x2 = x1 + (self.width // 2) + 1
		h2 = self.height
		w2 = (self.width // 2) - (1 - (self.width % 2))
		return( WindowArea(y1,x1,h1,w1), WindowArea(y2,x2,h2,w2), x2-1 )

	def split_vertically(self):
		y1 = self.y
		x1 = self.x
		h1 = self.height // 2
		w1 = self.width
		# height=22: 1,0,22,100: 1,0,11,100 & |y=12| & 13,0,10,100
		# height=23: 1,0,23,100: 1,0,11,100 & |y=12| & 13,0,11,100 
		y2 = y1 + (self.height // 2) + 1
		x2 = self.x
		h2 = (self.height // 2) - (1 - (self.height % 2))
		w2 = self.width
		return( WindowArea(y1,x1,h1,w1), WindowArea(y2,x2,h2,w2), y2-1 )

	def unpack(self):
		return (self.y, self.x, self.height, self.width)

	# returns (y,x,w) where: (y,x) is the offert to place a text "No files selected" with a max-width=w
	def get_center_of_area(self):
		start_y = self.y
		end_y = (self.y + self.height - 1)
		y = (start_y + end_y) // 2
		x = self.x
		w = self.width - 1
		return (y, x, w)

	@staticmethod
	def merge_horizontally(area1, area2):
		y1, x1, h1, w1 = area1.unpack()
		y2, x2, h2, w2 = area2.unpack()
		return WindowArea(y1, x1, h1, w1+w2+1)

	@staticmethod
	def merge_vertically(area1, area2):
		y1, x1, h1, w1 = area1.unpack()
		y2, x2, h2, w2 = area2.unpack()
		return WindowArea(y1, x1, h1+h2+1, w1)

class TabNode:
	def __init__(self, tab, parent, win, type, area, existing_editor = None):
		self.tab = tab
		self.parent = parent
		self.type = type
		self.win = win
		self.area = area
		if(self.type != TabNodeType.EDITOR): raise(Exception("TabNode:__init__() called with invalid NodeType"))
		if(existing_editor == None):
			self.editor = self.create_new_blank_editor()
		else:
			self.editor = existing_editor
		self.editor.parent = self
		y, x, h, w = self.area.unpack()
		self.editor.resize(y, x, h, w)
		self.children = None

	def readjust(self, area):
		self.area = area
		if(self.type == TabNodeType.EDITOR):
			y, x, height, width = self.area.unpack()
			self.editor.resize(y, x, height, width, True)
		else:
			if(self.type == TabNodeType.HORIZONTAL_SPLIT):
				split_area1, split_area2, self.border_x = self.area.split_horizontally()
			elif(self.type == TabNodeType.VERTICAL_SPLIT):
				split_area1, split_area2, self.border_y = self.area.split_vertically()
			
			self.children[0].readjust(split_area1)
			self.children[1].readjust(split_area2)

	def create_new_blank_editor(self):
		ed = Editor(self, self.area)
		bid, buffer = self.tab.manager.app.buffers.create_new_buffer()
		ed.set_buffer(bid, buffer)
		return ed

	def addstr(self, y, x, text, style):
		self.win.addstr(y, x, text, style)

	def draw_border(self):
		if(self.type == TabNodeType.HORIZONTAL_SPLIT):
			for y in range(self.area.y, self.area.y + self.area.height):
				self.win.addstr(y, self.border_x, BORDER_VERTICAL, gc("inner-border"))
		elif(self.type == TabNodeType.VERTICAL_SPLIT):
			self.win.addstr(self.border_y, self.area.x, (BORDER_HORIZONTAL * self.area.width), gc("inner-border"))

	def draw_junction(self, caller):
		if(self.type == TabNodeType.EDITOR): return
		if(self.type == caller.type): return		# horizontal split followed by another horizontal split do not require any junction borders

		border_char = None
		if(self.type == TabNodeType.HORIZONTAL_SPLIT):
			# caller type is vertical split
			if(self.children[0].type == self.children[1].type):
				border_char = BORDER_CROSSROADS
			elif(self.children[0] == caller):
				border_char = BORDER_SPLIT_LEFT
			elif(self.children[1] == caller):
				border_char = BORDER_SPLIT_RIGHT

			self.win.addstr(caller.border_y, self.border_x, border_char, gc("inner-border"))
		elif(self.type == TabNodeType.VERTICAL_SPLIT):
			# caller type is horizontal split
			if(self.children[0].type == self.children[1].type):
				border_char = BORDER_CROSSROADS
			elif(self.children[0] == caller):
				border_char = BORDER_SPLIT_TOP
			elif(self.children[1] == caller):
				border_char = BORDER_SPLIT_BOTTOM

			self.win.addstr(self.border_y, caller.border_x, border_char, gc("inner-border"))
		
	def get_successor(self):
		temp = self
		while(self.tab != temp.parent and temp == temp.parent.children[1]):
			temp = temp.parent
		if(self.tab != temp.parent): temp = temp.parent.children[1]
		while(temp.type != TabNodeType.EDITOR):
			temp = temp.children[0]
		return temp

	def get_predecessor(self):
		temp = self
		while(self.tab != temp.parent and temp == temp.parent.children[0]):
			temp = temp.parent
		if(self.tab != temp.parent): temp = temp.parent.children[0]
		while(temp.type != TabNodeType.EDITOR):
			temp = temp.children[1]
		return temp

	def bottom_up_readjust(self):				# called from an editor only
		self.tab.bottom_up_readjust()

	def bottom_up_repaint(self):				# called from an editor only
		self.win.repaint()
		
	def repaint(self):							# called from parent
		self.draw_border()
		if(self.type == TabNodeType.EDITOR):
			if(self.editor.buffer == None):
				y, x, w = self.area.get_center_of_area
				self.win.addstr(y, x, "No files selected".center(w), gc("disabled"))
			else:
				self.editor.repaint()
		else:
			self.children[0].repaint()
			self.children[1].repaint()
			self.parent.draw_junction(self)

	def split_horizontally(self):
		if(self.type != TabNodeType.EDITOR): return
		split_area1, split_area2, self.border_x = self.area.split_horizontally()
		y, x, height, width = split_area1.unpack()
		self.editor.resize(y, x, height, width, True)
		self.children = [ 
			TabNode(self.tab, self, self.win, TabNodeType.EDITOR, split_area1, self.editor),
			TabNode(self.tab, self, self.win, TabNodeType.EDITOR, split_area2)
		]
		self.editor = None
		self.type = TabNodeType.HORIZONTAL_SPLIT
		return self.children[0].editor

	def split_vertically(self):
		if(self.type != TabNodeType.EDITOR): return
		split_area1, split_area2, self.border_y = self.area.split_vertically()
		y, x, height, width = split_area1.unpack()
		self.editor.resize(y, x, height, width, True)
		self.children = [ 
			TabNode(self.tab, self, self.win, TabNodeType.EDITOR, split_area1, self.editor),
			TabNode(self.tab, self, self.win, TabNodeType.EDITOR, split_area2)
		]
		self.editor = None
		self.type = TabNodeType.VERTICAL_SPLIT
		return self.children[0].editor

	def merge_horizontally(self, caller = None):
		if(self.type == TabNodeType.EDITOR):
			self.parent.merge_horizontally(caller = self)
		elif(self.type == TabNodeType.HORIZONTAL_SPLIT and caller != None and caller.type == TabNodeType.EDITOR):
			self.type = TabNodeType.EDITOR
			self.editor = caller.editor
			self.editor.parent = self
			y, x, h, w = self.area.unpack()
			self.editor.resize(y, x, h, w)
			self.children = None
		else:
			return		# cannot merge

	def merge_vertically(self, caller = None):
		if(self.type == TabNodeType.EDITOR):
			self.parent.merge_vertically(caller = self)
		elif(self.type == TabNodeType.VERTICAL_SPLIT and caller != None and caller.type == TabNodeType.EDITOR):
			self.type = TabNodeType.EDITOR
			self.editor = caller.editor
			self.editor.parent = self
			y, x, h, w = self.area.unpack()
			self.editor.resize(y, x, h, w)
			self.children = None
		else:
			return		# cannot merge

class WindowTab:
	def __init__(self, manager, win, screen_height, screen_width):
		self.manager = manager
		self.win = win
		self.screen_height = screen_height
		self.screen_width = screen_width
		self.root = TabNode(self, self, win, TabNodeType.EDITOR, WindowArea(1,0,screen_height-2,screen_width))
		self.active_editor = self.root.editor
		self.active_editor.focus()

	def bottom_up_readjust(self):			# called from TabNode only
		self.manager.bottom_up_readjust()

	def readjust(self, screen_height, screen_width):
		self.screen_height = screen_height
		self.screen_width = screen_width
		self.root.readjust( WindowArea(1, 0, screen_height-2, screen_width) )

	def close_active_editor(self):
		active_tab_node = self.active_editor.parent
		if(active_tab_node == self.root):
			return False			# cannot close by itself; must be destroyed by parent
		parent_node = active_tab_node.parent
		if(parent_node.type == TabNodeType.HORIZONTAL_SPLIT):
			parent_node.merge_horizontally(active_tab_node)
			return True
		elif(parent_node.type == TabNodeType.VERTICAL_SPLIT):
			parent_node.merge_vertically(active_tab_node)
			return True
		raise(Exception("Error in WindowTab:close_active_editor()"))
	
	# this function is required for the recursion as a dummy 
	# else self.parent.merge_vertically() call will fail in TabNode
	def draw_junction(self, caller):
		pass		# no need to draw junction border as there is only 1 editor

	def get_active_editor(self):
		return self.active_editor

	# returns the total number of editors
	def get_editor_count(self):
		return self.__get_editor_count(self.root)

	# recursively find the # of editors
	def __get_editor_count(self, r):
		if(r.type == TabNodeType.EDITOR):
			return 1
		else:
			return self.__get_editor_count(r.children[0]) + self.__get_editor_count(r.children[1])

	def switch_to_next_editor(self):
		self.active_editor.blur()
		self.active_editor = self.active_editor.parent.get_successor().editor
		self.active_editor.focus()

	def switch_to_previous_editor(self):
		self.active_editor.blur()
		self.active_editor = self.active_editor.parent.get_predecessor().editor
		self.active_editor.focus()

	def repaint(self):				# Called from WindowManager
		self.root.repaint()

	def split_horizontally(self):
		self.active_editor.blur()
		self.active_editor = self.active_editor.parent.split_horizontally()
		self.active_editor.focus()

	def split_vertically(self):
		self.active_editor.blur()
		self.active_editor = self.active_editor.parent.split_vertically()
		self.active_editor.focus()

	# this function is both called by TopLevelWindow (caller=None) and by TabNode (caller!=None)
	def merge_horizontally(self, caller = None):
		if(caller == None): 
			self.active_editor.blur()
			self.active_editor.parent.merge_horizontally()
			self.active_editor.focus()
	
	# this function is both called by TopLevelWindow (caller=None) and by TabNode (caller!=None)
	def merge_vertically(self, caller = None):
		if(caller == None): 
			self.active_editor.blur()
			self.active_editor.parent.merge_vertically()
			self.active_editor.focus()

# There will be a single instance of WindowManager (held by app.main_window [TopLevelWindow])
# WindowManager will contain 1 or more WindowTab
# WindowTab will contain 1 root TabNode
# TabNode will contain either 1 editor, or 2 child TabNode (split horizontally/vertically)

class WindowManager:
	def __init__(self, app, win):
		self.app = app				# AshEditorApp
		self.win = win				# TopLevelWindow
		self.screen_height = self.app.screen_height
		self.screen_width = self.app.screen_width
		self.tabs = list()
		self.active_tab_index = -1

	def bottom_up_readjust(self):			# called from WindowTab only
		self.win.readjust()

	def readjust(self):
		self.screen_height = self.app.screen_height
		self.screen_width = self.app.screen_width
		for t in self.tabs:
			t.readjust(self.screen_height, self.screen_width)

	def get_active_tab(self):
		if(self.active_tab_index == -1):
			return None
		else:
			return self.tabs[self.active_tab_index]

	def get_active_tab_index(self):
		return self.active_tab_index

	# add tab after the current tab
	def add_tab(self):
		new_tab = WindowTab(self, self.win, self.screen_height, self.screen_width)
		self.tabs.insert(self.active_tab_index + 1, new_tab)
		self.active_tab_index += 1

	def remove_tab(self, tab_index):
		self.tabs.pop(tab_index)
		if(self.active_tab_index == tab_index):
			self.active_tab_index -= 1
		if(self.active_tab_index == -1 and len(self.tabs) > 0):
			self.active_tab_index = len(self.tabs) - 1

	def close_active_tab(self):
		if(self.active_tab_index == -1): return
		self.tabs.pop(self.active_tab_index)
		if(len(self.tabs) == 0):
			self.active_tab_index = -1
		elif(self.active_tab_index >= len(self.tabs)): 
			self.active_tab_index = 0
		self.get_active_editor().focus()
	
	def close_active_editor(self):
		if(self.active_tab_index == -1): return
		self.get_active_editor().blur()
		success = self.tabs[self.active_tab_index].close_active_editor()
		if(not success): 
			return self.close_active_tab()
		else:
			self.get_active_editor().focus()
			return True

	def repaint(self):					# called by main_window
		if(self.active_tab_index == -1): return
		self.tabs[self.active_tab_index].repaint()

	def get_tabs_info(self):
		info = list()
		for i, t in enumerate(self.tabs):
			info.append( ( "Tab-" + str(i+1), t.get_editor_count() ) )
		return info

	def get_tab_count(self):
		return len(self.tabs)

	def get_active_editor(self):
		if(self.active_tab_index == -1): return None
		return self.tabs[self.active_tab_index].get_active_editor()

	def switch_to_tab(self, tab_index):
		if(tab_index >= 0 and tab_index < len(self.tabs)):
			self.active_tab_index = tab_index

	def switch_to_next_tab(self):
		if(self.active_tab_index == -1): return
		self.active_tab_index = (self.active_tab_index + 1) % len(self.tabs)

	def switch_to_previous_tab(self):
		if(self.active_tab_index == -1): return
		self.active_tab_index = (self.active_tab_index - 1) % len(self.tabs)

	def switch_to_next_editor(self):
		if(self.active_tab_index == -1): return
		self.tabs[self.active_tab_index].switch_to_next_editor()

	def switch_to_previous_editor(self):
		if(self.active_tab_index == -1): return
		self.tabs[self.active_tab_index].switch_to_previous_editor()

	def get_editor_count(self):
		total_count = 0
		for t in self.tabs:
			total_count += t.get_editor_count()
		return total_count

	def merge_horizontally(self):
		if(self.active_tab_index == -1): return
		self.tabs[self.active_tab_index].merge_horizontally()
	
	def merge_vertically(self):
		if(self.active_tab_index == -1): return
		self.tabs[self.active_tab_index].merge_vertically()

	def split_horizontally(self):
		if(self.active_tab_index == -1): return
		self.tabs[self.active_tab_index].split_horizontally()		

	def split_vertically(self):
		if(self.active_tab_index == -1): return
		self.tabs[self.active_tab_index].split_vertically()