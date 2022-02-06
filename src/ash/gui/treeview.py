# ---------------------------------------------------------------------------------------------
#  Copyright (c) Akash Nag. All rights reserved.
#  Licensed under the MIT License. See LICENSE.md in the project root for license information.
# ---------------------------------------------------------------------------------------------

# This module implements the TreeView widget

from ash import *
from ash.gui import *
from ash.gui.listbox import *
from ash.core.bufferManager import *
from ash.core.gitRepo import *

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

	# return True if the node represents a directory
	def is_dir(self):
		return (True if self.type == "d" else False)

	# add a child node under this directory-node
	def add_child_node(self, child_node):
		if(self.children != None): self.children.append(child_node)

	# collapse this directory-node
	def collapse(self):
		if(self.expanded != None): self.expanded = False

	# expand this directory-node
	def expand(self):
		if(self.expanded != None): self.expanded = True

	# return the display-name for this node
	def __str__(self):
		title = get_file_title(self.path)
		if(self.is_dir()):
			return ("\u229f" if self.expanded else "\u229e")  + "   " + title
		else:
			return title

	# returns the path of the file/directory represented by this node
	def __repr__(self):
		get_file_title(self.path)

	def get_dirname_with_gitstatus(self, git_repo):
		title = get_file_title(self.path)
		gsc = None

		if(self.is_dir()):
			if(self.parent == None):
				rds = git_repo.is_dirty()
				if(rds):
					gs = UNSAVED_BULLET + " "
					gsc = gc("gitstatus-M")
				else:
					gs = ""
			else:
				gs, gsc = GitRepo.format_status_type(git_repo.get_directory_status(self.path))
				if(gs != None): 
					gs += " "
				else:
					gs = ""

			return (("\u229f" if self.expanded else "\u229e")  + "   " + gs + title, gsc, 4)
		else:
			return None		# this fn is not for files
	
class TreeView(Widget):
	def __init__(self, parent, y, x, width, row_count, buffer_manager, project_dir, supports_colors=True):
		super().__init__(WIDGET_TYPE_LISTBOX)
		self.parent = parent
		self.y = y
		self.x = x
		self.width = width
		self.height = row_count
		self.row_count = row_count
		self.buffer_manager = buffer_manager
		self.project_dir = project_dir
		self.supports_colors = supports_colors
		self.theme = gc("global-default")
		self.focus_theme = gc("formfield-focussed")
		self.sel_blur_theme = gc("formfield-selection-blurred")		
		self.is_in_focus = False
		self.git_repo = GitRepo(self.project_dir)
		self.search_text = None
		self.refresh()

	# refresh the tree
	def refresh(self, maintain_selindex = False):
		self.git_repo.refresh(True)
		self.refresh_glob()
		self.tree_root = self.form_tree()
		self.form_list_items()
		if(not maintain_selindex): self.sel_index = 0
		self.start = 0
		self.end = min([self.row_count, len(self.items)])
		self.repaint()
	
	# finds all files and subdirectories in the tree
	def refresh_glob(self):
		self.files = list()
		self.dirs = list()				
		all_files = glob.glob(self.project_dir + "/**/*", recursive=True)
		
		for f in all_files:
			if(not os.path.isfile(f)): continue
			if(not should_ignore_file(f)): self.files.append(f)
			dir_list = get_relative_subdirectories(self.project_dir, f)

			for d in dir_list:
				if(d not in self.dirs and not should_ignore_directory(d)):
					self.dirs.append(d)
		
		for d in os.walk(self.project_dir):
			if(d[0] not in self.dirs and not should_ignore_directory(d[0])):
				self.dirs.append(d[0])
	
	# form the tree-root and add subnodes recursively
	def form_tree(self):
		root_node = TreeNode(None, self.project_dir)
		self.form_children(root_node)
		return root_node

	# add subnodes recursively
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

	# form the root display-node and add its children recursively
	def form_list_items(self):
		self.items = list()		# contains tuple(text, node_obj, style, offset(int) )
		self.tags = list()

		disp_text, disp_style, offset = self.tree_root.get_dirname_with_gitstatus(self.git_repo)
		self.items.append( (disp_text, self.tree_root, disp_style, offset) )
		self.tags.append(self.tree_root.type + ":" + self.tree_root.path)
		if(self.tree_root.expanded): 
			self.form_sublist_items(self.tree_root, 0, " " * INDENT_SIZE)
	
	# form the displayed child nodes recursively
	def form_sublist_items(self, root_node, root_level, space):
		if(root_node.children == None): return
		n = len(root_node.children)
		for index, c in enumerate(root_node.children):
			marker = LINE_EDGE if index == n-1 else LINE_SPLIT
			extra_space = marker
			gs = "  "
			gsc = None
			if(not c.is_dir()): 
				if(self.search_text != None and str(c).lower().find(self.search_text) < 0): continue
				if(not BufferManager.is_binary(c.path)):
					buffer = self.buffer_manager.get_buffer_by_filename(c.path)
					save_status = buffer.save_status if buffer != None else True
					extra_space += (LINE_HORIZONTAL * (INDENT_SIZE-3)) + " " + ("" if save_status else UNSAVED_BULLET) + " "
				else:
					extra_space += (LINE_HORIZONTAL * (INDENT_SIZE-3)) + "   "
				gs, gsc = GitRepo.format_status_type(self.git_repo.get_file_status(c.path))
				gs += "  "
				self.items.append( (space + extra_space + gs + str(c), c, gsc, len(space+extra_space)) )
			else:
				disp_text, gsc, offset = c.get_dirname_with_gitstatus(self.git_repo)
				self.items.append( (space + extra_space + disp_text, c, gsc, len(space+extra_space) + offset) )

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
			if(i < 0 or i >= len(self.items)): break
			disp_text, node_obj, style, text_offset = self.items[i]
			if(style == None): style = self.theme

			n = 2 + len(disp_text)
			if(n > self.width):
				text = " " + disp_text[0:self.width-2] + " "
			else:
				text = " " + disp_text + (" " * (self.width-n+1))

			if(i == self.sel_index):
				if(self.is_in_focus):
					self.parent.addstr(self.y + i - self.start, self.x, text, self.focus_theme | (0 if self.supports_colors else curses.A_REVERSE))
				else:
					self.parent.addstr(self.y + i - self.start, self.x, text, self.sel_blur_theme | (0 if self.supports_colors else curses.A_BOLD))
			else:				
				self.parent.addstr(self.y + i - self.start, self.x, text[0:text_offset], self.theme)
				self.parent.addstr(self.y + i - self.start, self.x + text_offset, text[text_offset:], style)

		
	# handle key presses
	def perform_action(self, ch):
		self.focus()
		
		n = len(self.items)
		sel_item_obj = self.items[self.sel_index][1]

		if(KeyBindings.is_key(ch, "LIST_MOVE_SELECTION_UP")):
			# UP ARROW
			if(self.sel_index <= 0):
				self.sel_index = 0
			else:
				self.sel_index = (self.sel_index - 1) % n
		elif(KeyBindings.is_key(ch, "LIST_MOVE_SELECTION_DOWN")):
			# DOWN ARROW
			if(self.sel_index < n-1):
				self.sel_index = (self.sel_index + 1) % n
		elif(KeyBindings.is_key(ch, "LIST_MOVE_TO_PREVIOUS_PAGE")):
			# PAGE UP
			if(self.sel_index > self.row_count):
				self.sel_index -= self.row_count
			else:
				self.sel_index = 0
		elif(KeyBindings.is_key(ch, "LIST_MOVE_TO_NEXT_PAGE")):
			# PAGE DOWN
			if(self.sel_index < len(self.items) - self.row_count):
				self.sel_index += min([self.row_count, len(self.items)-1])
			else:
				self.sel_index = len(self.items)-1
		elif(KeyBindings.is_key(ch, "COLLAPSE_DIRECTORY")  and sel_item_obj.is_dir() and sel_item_obj.expanded):
			# PLUS
			sel_item_obj.collapse()
			self.mini_refresh()
		elif(KeyBindings.is_key(ch, "EXPAND_DIRECTORY") and sel_item_obj.is_dir() and not sel_item_obj.expanded):
			# MINUS
			sel_item_obj.expand()
			self.mini_refresh()
		elif(KeyBindings.is_key(ch, "REFRESH_DIRECTORY_TREE")):
			# REFRESH
			self.refresh()
			return
		elif(KeyBindings.is_key(ch, "CREATE_NEW_DIRECTORY")):
			# NEW DIRECTORY
			self.create_new_directory()
		elif(KeyBindings.is_key(ch, "CREATE_NEW_FILE")):
			# NEW FILE
			self.create_new_file()
		elif(KeyBindings.is_key(ch, "DELETE_FILE")):
			# DELETE
			if(self.sel_index == 0):
				self.parent.parent.app.show_error("Cannot delete project root")
			else:
				self.delete_sel_item()
		elif(KeyBindings.is_key(ch, "RENAME_FILE")):
			# RENAME
			if(self.sel_index == 0):
				self.parent.parent.app.show_error("Cannot rename project root")
			else:
				self.rename_sel_item()
		else:
			beep()

		self.repaint()

	def search(self, search_text):
		if(search_text != None):
			search_text = search_text.strip().lower()
			if(len(search_text) == 0): search_text = None
		self.search_text = search_text
		self.mini_refresh()

	# refresh on collapse/expand operation
	def mini_refresh(self):
		self.form_list_items()
		self.start = 0
		self.end = min([self.row_count, len(self.items)])

	# create a new directory under the selected node
	def create_new_directory(self):
		parent_dir = self.get_sel_filepath()
		if(os.path.isfile(parent_dir)): parent_dir = os.path.dirname(parent_dir)
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
	
	# create a new file under the selected node
	def create_new_file(self):
		parent_dir = self.get_sel_filepath()
		if(os.path.isfile(parent_dir)): parent_dir = os.path.dirname(parent_dir)
		fn = self.parent.parent.app.prompt("CREATE FILE", "Enter a new filename: ")
		if(fn != None and len(fn) > 0):
			filename = parent_dir + "/" + fn
			if(os.path.isfile(filename)):
				self.parent.parent.app.show_error("The file already exists!")
				return
			try:
				f = codecs.open(filename, "w", "utf-8")
				f.write("")
				f.close()
				self.refresh(True)
			except:
				self.parent.parent.app.show_error("An error occurred while creating file")
				
	# move the selected file/directory to the trash
	def delete_sel_item(self):
		fp = self.get_sel_filepath()
		if(self.parent.parent.app.ask_question("DELETE", "Are you sure you want to delete this item?")):
			try:
				send2trash(fp)
				self.refresh()
			except:
				self.parent.parent.app.show_error("An error occurred while deleting item")
	
	# rename the selected file/directory
	def rename_sel_item(self):
		fp = self.get_sel_filepath()
		new_name = self.parent.parent.app.prompt("RENAME", "Enter a new name: ", get_file_title(fp))
		if(new_name == get_file_title(fp)): return

		dir = os.path.dirname(fp)
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

	def on_click(self, y, x):
		if(len(self.items) > y + self.start):
			self.sel_index = y + self.start
			self.repaint()