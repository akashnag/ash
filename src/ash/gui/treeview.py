# ---------------------------------------------------------------------------------------------
#  Copyright (c) Akash Nag. All rights reserved.
#  Licensed under the MIT License. See LICENSE.md in the project root for license information.
# ---------------------------------------------------------------------------------------------

# This module implements the TreeView widget

from ash import *
from ash.gui import *
from ash.gui.listbox import *
from ash.core.bufferManager import *

import glob
import os
from send2trash import send2trash

INDENT_SIZE		= 4

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

	def refresh(self, maintain_selindex = False):
		self.refresh_glob()
		self.ensure_files_have_buffers()
		self.tree_root = self.form_tree()
		self.form_list_items()
		if(not maintain_selindex): self.sel_index = 0
		self.start = 0
		self.end = min([self.row_count, len(self.items)])
		self.repaint()

	def ensure_files_have_buffers(self):		
		for f in self.files:
			if(BufferManager.is_binary(f)): continue
			has_backup = BufferManager.backup_exists(f)
			if(not self.buffer_manager.does_file_have_its_own_buffer(f)):
				self.buffer_manager.create_new_buffer(filename=f, has_backup=has_backup)

	def refresh_glob(self):
		self.files = list()
		self.dirs = list()				
		all_files = glob.glob(self.project_dir + "/**/*.*", recursive=True)
		for f in all_files:
			self.files.append(f)
			dir_list = get_relative_subdirectories(self.project_dir, f)
			for d in dir_list:
				if(d not in self.dirs): self.dirs.append(d)
		for d in os.walk(self.project_dir):
			if(d[0] not in self.dirs): self.dirs.append(d[0])
	
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
		if(self.tree_root.expanded): 
			self.form_sublist_items(self.tree_root, 0, " " * INDENT_SIZE)
	
	def form_sublist_items(self, root_node, root_level, space):
		if(root_node.children == None): return
		n = len(root_node.children)
		for index, c in enumerate(root_node.children):
			marker = LINE_EDGE if index == n-1 else LINE_SPLIT
			extra_space = marker
			if(not c.is_dir()): 
				if(not BufferManager.is_binary(c.path)):
					buffer = self.buffer_manager.get_buffer_by_filename(c.path)
					save_status = buffer.save_status
					extra_space += (LINE_HORIZONTAL * (INDENT_SIZE-3)) + " " + (" " if save_status else UNSAVED_BULLET) + " "
				else:
					extra_space += (LINE_HORIZONTAL * (INDENT_SIZE-3)) + "   "
			self.items.append( (space + extra_space + str(c), c) )
			self.tags.append(c.type + ":" + c.path)
			if(c.is_dir() and c.expanded): 
				self.form_sublist_items(c, root_level + 1, space + (LINE_VERTICAL if marker == LINE_SPLIT else " ") + (" " * (INDENT_SIZE-1)))

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
		
		if(count <= self.row_count):
			self.start = 0
			self.end = count
		elif(self.sel_index == -1):
			self.start = 0
			self.end = self.row_count
		else:
			if(self.sel_index < self.start):
				self.start = self.sel_index
				self.end = min([self.start + self.row_count, count])
			elif(self.sel_index >= self.end):
				self.end = self.sel_index + 1
				self.start = max([self.end - self.row_count, 0])
			
		for i in range(self.start, self.end):
			disp_text, node_obj = self.items[i]

			n = 2 + len(disp_text)
			if(n > self.width):
				text = " " + disp_text[0:self.width-2] + " "
			else:
				text = " " + disp_text + (" " * (self.width-n+1))

			if(i == self.sel_index):
				if(self.is_in_focus):
					self.parent.addstr(self.y + i - self.start, self.x, text, self.focus_theme)
				else:
					self.parent.addstr(self.y + i - self.start, self.x, text, self.sel_blur_theme)
			else:				
				self.parent.addstr(self.y + i - self.start, self.x, text, self.theme)

		
	# handle key presses
	def perform_action(self, ch):
		self.focus()
		
		n = len(self.items)
		sel_item_obj = self.items[self.sel_index][1]

		if(ch == curses.KEY_UP):
			if(self.sel_index <= 0):
				self.sel_index = 0
			else:
				self.sel_index = (self.sel_index - 1) % n
		elif(ch == curses.KEY_DOWN):
			if(self.sel_index < n-1):
				self.sel_index = (self.sel_index + 1) % n
		elif(ch == curses.KEY_PPAGE):		# PgUp
			if(self.sel_index > self.row_count):
				self.sel_index -= self.row_count
			else:
				self.sel_index = 0
		elif(ch == curses.KEY_NPAGE):		# PgDown
			if(self.sel_index < len(self.items) - self.row_count):
				self.sel_index += min([self.row_count, len(self.items)-1])
			else:
				self.sel_index = len(self.items)-1
		elif(str(chr(ch)) == "+" and sel_item_obj.is_dir() and sel_item_obj.expanded):
			sel_item_obj.collapse()
			self.mini_refresh()
		elif(str(chr(ch)) == "-" and sel_item_obj.is_dir() and not sel_item_obj.expanded):
			sel_item_obj.expand()
			self.mini_refresh()
		elif(is_ctrl(ch, "R")):
			self.refresh()
			return
		elif(is_ctrl(ch, "D")):
			self.create_new_directory()
		elif(is_ctrl(ch, "N")):
			self.create_new_file()
		elif(ch == curses.KEY_DC):
			if(self.sel_index == 0):
				self.parent.parent.app.show_error("Cannot delete project root")
			else:
				self.delete_sel_item()
		elif(is_func(ch, 2)):
			if(self.sel_index == 0):
				self.parent.parent.app.show_error("Cannot rename project root")
			else:
				self.rename_sel_item()
		else:
			beep()

		self.repaint()

	def mini_refresh(self):
		self.form_list_items()
		self.start = 0
		self.end = min([self.row_count, len(self.items)])

	def create_new_directory(self):
		parent_dir = self.get_sel_filepath()
		if(os.path.isfile(parent_dir)): parent_dir = get_file_directory(parent_dir)
		fn = self.parent.parent.app.prompt("CREATE DIRECTORY", "Enter a new directory name: ")
		if(fn != None and len(fn) > 0):
			filename = parent_dir + "/" + fn
			if(os.path.isfile(filename) or os.path.isdir(filename)):
				self.parent.parent.app.show_error("The file already exists!")
			else:
				try:
					os.makedirs(filename)
					self.refresh(True)
				except:
					self.parent.parent.app.show_error("An error occurred while creating directory")				
	
	def create_new_file(self):
		parent_dir = self.get_sel_filepath()
		if(os.path.isfile(parent_dir)): parent_dir = get_file_directory(parent_dir)
		fn = self.parent.parent.app.prompt("CREATE FILE", "Enter a new filename: ")
		if(fn != None and len(fn) > 0):
			filename = parent_dir + "/" + fn
			if(os.path.isfile(filename)):
				self.parent.parent.app.show_error("The file already exists!")
				return
			try:
				fp = open(filename, "wt")
				fp.close()
				self.refresh(True)
			except:
				self.parent.parent.app.show_error("An error occurred while creating file")
				

	def delete_sel_item(self):
		fp = self.get_sel_filepath()
		if(self.parent.parent.app.ask_question("DELETE", "Are you sure you want to delete this item?")):
			try:
				send2trash(fp)
				self.refresh()
			except:
				self.parent.parent.app.show_error("An error occurred while deleting item")
	
	def rename_sel_item(self):
		fp = self.get_sel_filepath()
		new_name = self.parent.parent.app.prompt("RENAME", "Enter a new name: ", get_file_title(fp))
		if(new_name == get_file_title(fp)): return

		dir = get_file_directory(fp)
		new_fp = dir + "/" + new_name

		if(os.path.isfile(new_fp) or os.path.isdir(new_fp)):
			self.parent.parent.app.show_error("The selected file/directory already exists")
		else:
			try:
				os.rename(fp, new_fp)
				self.refresh()
			except:
				self.parent.parent.app.show_error("An error occurred during renaming")


	# returns the text of the selected item
	def __str__(self):
		return self.get_sel_filepath()