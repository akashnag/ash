# ---------------------------------------------------------------------------------------------
#  Copyright (c) Akash Nag. All rights reserved.
#  Licensed under the MIT License. See LICENSE.md in the project root for license information.
# ---------------------------------------------------------------------------------------------

# This module implements the TreeView widget

from ash.gui import *
from ash.gui.listbox import *
from ash.formatting.colors import *

from ash.core.utils import *
from ash.core.bufferManager import *

import glob
import os

class TreeNode:
	def __init__(self, parent, path):
		self.parent = parent
		self.path = path
		self.type = "f" if os.path.isfile(self.path) else "d"
		self.expanded = None
		if(self.type == "d"): self.expanded = True
		if(self.type == "f"):
			self.children = None
		else:
			self.children = list()

	def is_dir(self):
		return (True if self.type == "d" else False)

	def add_child_node(self, child_node):
		if(self.children != None): self.children.append(child_node)

	def collapse(self):
		if(self.expanded != None): self.expanded = False

	def expand(self):
		if(self.expanded != None): self.expanded = True

	def __str__(self):
		title = get_file_title(self.path)
		if(self.is_dir()):
			return "[" + ("-" if self.expanded else "+")  + "] " + title
		else:
			return title

	def __repr__(self):
		pass

class TreeView(Widget):
	def __init__(self, parent, y, x, width, row_count, buffer_manager, project_dir):
		super().__init__(WIDGET_TYPE_LISTBOX)
		self.parent = parent
		self.y = y
		self.x = x
		self.width = width
		self.row_count = row_count
		self.buffer_manager = buffer_manager
		self.project_dir = project_dir
		self.theme = gc("formfield")
		self.focus_theme = gc("formfield-focussed")
		self.sel_blur_theme = gc("formfield-selection-blurred")		
		self.is_in_focus = False		
		self.refresh()

	def refresh(self):
		self.refresh_glob()
		self.ensure_files_have_buffers()
		self.tree_root = self.form_tree()
		self.form_list_items()
		self.sel_index = 0
		self.repaint()

	def ensure_files_have_buffers(self):		
		for f in self.files:
			has_backup = BufferManager.backup_exists(f)
			if(not self.buffer_manager.does_file_have_its_own_buffer(f)):
				self.buffer_manager.create_new_buffer(filename=f, has_backup=has_backup)

	def refresh_glob(self):
		self.files = list()
		self.dirs = list()				
		all_files = glob.glob(self.project_dir + "/**/*.*", recursive=True)
		for f in all_files:
			self.files.append(f)
			dir = get_file_directory(f)
			if(dir not in self.dirs): self.dirs.append(dir)
	
	def form_tree(self):
		root_node = TreeNode(None, self.project_dir)
		self.form_children(root_node)
		return root_node

	def form_children(self, root_node):
		sub_dirs = sorted(filter_child_directories(root_node.path, self.dirs))
		sub_files = sorted(filter_child_directories(root_node.path, self.files))
		
		for d in sub_dirs:
			sd_node = TreeNode(root_node, d)
			root_node.add_child_node(sd_node)
			self.form_children(sd_node)

		for f in sub_files:
			sf_node = TreeNode(root_node, f)
			root_node.add_child_node(sf_node)

	def form_list_items(self):
		self.items = list()
		self.tags = list()		
		self.items.append( (str(self.tree_root), self.tree_root) )
		self.tags.append(self.tree_root.type + ":" + self.tree_root.path)
		if(self.tree_root.expanded): self.form_sublist_items(self.tree_root, 0);
	
	def form_sublist_items(self, root_node, root_level):
		if(root_node.children == None): return
		space = " " * (4 * (1 + root_level))
		for c in root_node.children:
			if(not c.is_dir()): extra_space = " " * 4
			self.items.append( (space + extra_space + str(c), c) )
			self.tags.append(c.type + ":" + c.path)
			if(c.is_dir() and c.expanded): self.form_sublist_items(c, root_level + 1);

	# when focus received
	def focus(self):
		self.is_in_focus = True
		self.repaint()

	# when focus lost
	def blur(self):
		self.is_in_focus = False
		self.repaint()

	# returns the index of the selected file in files_list, -1 if directory is selected
	def get_sel_index(self):
		return self.sel_index

	# returns the full path of the selected file
	def get_sel_filepath(self):
		return self.items[self.sel_index][1].path

	def get_sel_tag(self):
		return self.tags[self.sel_index]

	# draw the listbox
	def repaint(self):
		if(self.is_in_focus): curses.curs_set(False)
		
		count = len(self.items)
		start = 0
		end = min([self.row_count, count])

		if(count <= self.row_count):
			start = 0
			end = count
		elif(self.sel_index == -1):
			start = 0
			end = self.row_count
		else:
			if(self.sel_index < start):
				start = self.sel_index
				end = min([start + self.row_count, count])
			elif(self.sel_index >= end):
				end = self.sel_index + 1
				start = max([end - self.row_count, 0])
			
		for i in range(start, end):
			disp_text, node_obj = self.items[i]

			n = 2 + len(disp_text)
			if(n > self.width):
				text = " " + disp_text[0:self.width-2] + " "
			else:
				text = " " + disp_text + (" " * (self.width-n+1))

			if(i == self.sel_index):
				if(self.is_in_focus):
					self.parent.addstr(self.y + i - start, self.x, text, self.focus_theme)
				else:
					self.parent.addstr(self.y + i - start, self.x, text, self.sel_blur_theme)
			else:				
				self.parent.addstr(self.y + i - start, self.x, text, self.theme)

		
	# handle key presses
	def perform_action(self, ch):
		self.focus()
		
		n = len(self.items)
		sel_item_obj = self.items[self.sel_index][1]

		if(ch == curses.KEY_UP):
			if(self.sel_index == -1):
				self.sel_index = n-1
			else:
				self.sel_index = (self.sel_index - 1) % n
		elif(ch == curses.KEY_DOWN):
			self.sel_index = (self.sel_index + 1) % n
		elif(str(chr(ch)) == "+" and sel_item_obj.is_dir() and sel_item_obj.expanded):
			sel_item_obj.collapse()
			self.form_list_items()
			self.sel_index = 0
		elif(str(chr(ch)) == "-" and sel_item_obj.is_dir() and not sel_item_obj.expanded):
			sel_item_obj.expand()
			self.form_list_items()
			self.sel_index = 0
		elif(is_ctrl(ch, "R")):
			self.refresh()
			return
		else:
			beep()

		self.repaint()

	# returns the text of the selected item
	def __str__(self):
		return self.get_sel_filepath()