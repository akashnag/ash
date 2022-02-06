# ---------------------------------------------------------------------------------------------
#  Copyright (c) Akash Nag. All rights reserved.
#  Licensed under the MIT License. See LICENSE.md in the project root for license information.
# ---------------------------------------------------------------------------------------------

# This module implements a Grouped ListBox widget with collapseable items

from ash.gui import *
from ash.gui.cursorPosition import *
from ash.utils.keyUtils import *

class GroupedListItem:
	def __init__(self, text, filename):
		self.collapsed = False
		self.text = text
		self.filename = filename
		self.children = list()
		self.positions = list()

	def add_child(self, text, line_index, col_pos):
		self.children.append(text)
		self.positions.append(CursorPosition(line_index, col_pos))

	def __len__(self):
		if(self.collapsed):
			return 1
		else:
			return 1 + len(self.children)

	def __str__(self):
		if(self.collapsed):
			return "\u229e " + self.text
		else:
			return "\u229f " + self.text

	def get_sublist(self):
		if(self.collapsed):
			return None
		else:
			return self.children

class GroupedListBox(Widget):
	def __init__(self, parent, y, x, width, row_count, placeholder_text = None, callback = None, supports_colors=True):
		super().__init__(WIDGET_TYPE_LISTBOX)
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
		self.disp_items = list()
		self.should_highlight = list()
		self.theme = gc("global-default")
		self.focus_theme = gc("formfield-focussed")
		self.sel_blur_theme = gc("formfield-selection-blurred")
		self.sel_index = -1
		self.is_in_focus = False
		self.focussable = True
		self.list_start = 0
		self.list_end = 0
		self.count = 0
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
		
		if(self.sel_index == -1):
			self.list_start = 0
			self.list_end = min([self.row_count, self.count])
		elif(self.sel_index < self.list_start):
			self.list_start = self.sel_index
			self.list_end = min([self.list_start + self.row_count, self.count])
		elif(self.sel_index >= self.list_end):
			self.list_end = min([self.count, self.sel_index + 1])
			self.list_start = max([0, self.sel_index - self.row_count + 1])
			
		for i in range(self.list_start, self.list_end):
			n = 2 + len(str(self.disp_items[i]))
			if(n > self.width):
				text = " " + str(self.disp_items[i])[0:self.width-2] + " "
			else:
				text = " " + str(self.disp_items[i]) + (" " * (self.width-n+1))

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

		if(self.count == 0): self.parent.addstr(self.y + (self.row_count // 2), self.x, ("" if self.placeholder_text == None else self.placeholder_text).center(self.width), gc("disabled"))
	
	# handle key presses
	def perform_action(self, ch):
		self.focus()
		n = len(self.disp_items)

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
		elif(KeyBindings.is_key(ch, "FIND_NEXT")):
			self.handle_selected_file_open()
		elif(self.sel_index > -1 and self.tags[self.sel_index].startswith("p=")):
			i = int(self.tags[self.sel_index][2:])
			if(self.items[i].collapsed and KeyBindings.is_key(ch, "EXPAND_DIRECTORY")):
				self.items[i].collapsed = False
				self.render()
				self.repaint()
			elif(not self.items[i].collapsed and KeyBindings.is_key(ch, "COLLAPSE_DIRECTORY")):
				self.items[i].collapsed = True
				self.render()
				self.repaint()
			else:
				beep()
		else:
			beep()

		if(self.callback != None): self.callback(self.sel_index)
		self.repaint()

	def display(self, search_results, buffers):
		# data must be a dictionary indexed by buffer-IDs
		# each item contains a list of tuples(line_index, col_pos)
		app = self.parent.parent.app
		self.items = list()
		if(search_results == None):
			self.render()
			self.repaint()
			return

		for bid, data in search_results.items():
			buffer = buffers.get_buffer_by_id(bid)
			name = buffer.get_name()
			if(app.app_mode == APP_MODE_PROJECT):
				disp_name = get_relative_file_title(app.project_dir, name)
				if(disp_name == name): disp_name = get_file_title(name)
			else:
				disp_name = get_file_title(name)

			disp_name += " (" + str(len(data)) + " occurrences)"
			gli = GroupedListItem(disp_name, name)
			for d in data:
				line_index = d[0]
				col_pos = d[1]

				line_length = len(buffer.lines[line_index])
				context = buffer.lines[line_index][ max(0,col_pos-self.width) : min(line_length, col_pos+self.width) ]
				context = context.replace("\t", " ").replace("\n", " ").replace("\r","")
				disp_child = f"Line {line_index+1}, Col {col_pos+1}: {context}"
				gli.add_child(disp_child, line_index, col_pos)
			self.items.append(gli)

		self.render()
		self.repaint()
	
	def render(self):
		self.tags = list()
		self.should_highlight = list()
		self.disp_items = list()
		self.count = 0
		for i, item in enumerate(self.items):
			if(len(item) == 1 and not item.collapsed): continue
			self.count += len(item)
			self.disp_items.append(str(item))
			self.tags.append(f"p={i}")
			self.should_highlight.append(True)
			sublist = item.get_sublist()
			if(sublist == None): continue
			for j, child in enumerate(sublist):
				self.disp_items.append(str(child))
				self.tags.append(f"c={j};p={i}")
				self.should_highlight.append(False)
		
		if(self.sel_index < 0): 
			if(len(self.disp_items) > 0):
				self.sel_index = 0
				self.focussable = True
			else:
				self.sel_index = -1
				self.focussable = False
		
		self.list_start = 0
		self.list_end = min([self.row_count, len(self.disp_items)])
		
	def handle_selected_file_open(self):
		if(self.sel_index < 0): return
		mw = self.parent.parent
		app = mw.app
		tag = self.tags[self.sel_index]
		filename = None
		curpos = None
		if(tag.startswith("p=")):
			pli = int(tag[2:])
			gli = self.items[pli]
			filename = gli.filename
		elif(tag.startswith("c=")):
			temp = tag.split(";")
			pli = int(temp[1][2:])
			cli = int(temp[0][2:])
			gli = self.items[pli]
			filename = gli.filename
			curpos = gli.positions[cli]

		self.parent.handle_fileopen(filename, curpos)

	# returns the text of the selected item
	def __str__(self):
		return self.get_sel_text()

	def on_click(self, y, x):
		if(len(self.items) > y + self.list_start):
			self.sel_index = y + self.list_start
			tag = self.tags[self.sel_index]
			if(x == 1 and tag.startswith("p=")):
				i = int(tag[2:])
				self.items[i].collapsed = not self.items[i].collapsed
				self.render()
			self.repaint()