# ---------------------------------------------------------------------------------------------
#  Copyright (c) Akash Nag. All rights reserved.
#  Licensed under the MIT License. See LICENSE.md in the project root for license information.
# ---------------------------------------------------------------------------------------------

# This module implements the TreeView widget

from ash.widgets import *

class TreeView(Widget):
	def __init__(self, parent, y, x, width, row_count, files_list):
		super(ListBox, self).__init__(WIDGET_TYPE_LISTBOX)
		self.parent = parent
		self.y = y
		self.x = x
		self.width = width
		self.row_count = row_count
		self.files_list = files_list
		self.theme = gc(COLOR_FORMFIELD)
		self.focus_theme = gc(COLOR_FORMFIELD_FOCUSSED)
		self.sel_blur_theme = gc(COLOR_FORMFIELD_SELECTED_BLURRED)
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

	# returns the index of the selected file in files_list, -1 if directory is selected
	def get_sel_index(self):
		pass

	# returns the file-title of the selected file
	def get_sel_file_title(self):
		pass

	# returns the full path of the selected file
	def get_sel_filename(self):
		pass

	# draw the listbox
	def repaint(self):
		pass
	
	# handle key presses
	def perform_action(self, ch):
		if(self.files_list == None or len(self.files_list) == 0): return
		self.focus()
		
		if(ch == curses.KEY_UP):
			pass
		elif(ch == curses.KEY_DOWN):
			pass
		elif(str(chr(ch)) == "+"):		# expand directory if not already
			pass
		elif(str(chr(ch)) == "-"):		# collapse directory if not already
			pass
		else:
			beep()
		self.repaint()

	# returns the text of the selected item
	def __str__(self):
		return self.get_sel_filename()