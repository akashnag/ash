# ---------------------------------------------------------------------------------------------
#  Copyright (c) Akash Nag. All rights reserved.
#  Licensed under the MIT License. See LICENSE.md in the project root for license information.
# ---------------------------------------------------------------------------------------------

# This module implements the text-editor widget

from ash.widgets import *
from ash.widgets.utils.utils import *
from ash.widgets.utils.formatting import *
from ash.widgets.editorKeyHandler import *
from ash.widgets.editorUtility import *

# This class abstracts a position in the document
class CursorPosition:
	def __init__(self, y, x):
		self.y = y
		self.x = x

	def __str__(self):
		return "Ln " + str(self.y+1) + ", Col " + str(self.x+1)

# This is the text editor class
class Editor(Widget):
	def __init__(self, parent):
		super().__init__(WIDGET_TYPE_EDITOR, True, True)
		
		# initialize parent window
		self.parent = parent

		# initialize helper classes
		self.utility = EditorUtility(self)
		self.keyHandler = EditorKeyHandler(self)
				
		self.line_number_width = 6
						
		# set up the text and cursor data structures
		self.lines = [ "" ]
		self.curpos = CursorPosition(0,0)
		self.filename = None
		self.has_been_allotted_file = False
		self.save_status = False

		# set accepted charset
		self.separators = "~`!@#$%^&*()-_=+\\|[{]};:\'\",<.>/? "
		self.charset = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789"
		self.charset += self.separators
		self.newline = "\n"
		
		# set initial selection status
		self.selection_mode = False
		self.sel_start = CursorPosition(0,0)
		self.sel_end = CursorPosition(0,0)

		# set default tab size
		self.tab_size = 4
		
		# set up default color themes
		self.set_theme()
		self.set_comment_symbol(None, None, None)
		self.is_in_focus = False

		# use dummy values
		self.height = 0
		self.width = 0
		self.y = -1
		self.x = -1
		self.full_width = 0
		self.selection_mode = False
		self.curpos.x = -1
		self.curpos.y = -1
		self.col_start = -1
		self.col_end = 0
		self.line_start = -1
		self.line_end = -1
	
	# resize editor
	def resize(self, y, x, height, width):
		if(height == self.height and width == self.full_width): return

		self.y = y
		self.x = x
		self.height = height
		self.full_width = width
		self.width = self.full_width - self.line_number_width - 1
		
		self.selection_mode = False
		self.curpos.x = 0
		self.curpos.y = 0
		self.col_start = 0
		self.col_end = self.width
		self.line_start = 0
		self.line_end = self.height

	# when focus received
	def focus(self):
		self.is_in_focus = True
		self.repaint()

	# when focus lost
	def blur(self):
		self.is_in_focus = False
		self.repaint()

	# returns the current cursor position
	def get_cursor_position(self):
		return str(self.curpos)

	# set general text theme
	def set_theme(self):
		self.text_theme = gc(COLOR_DEFAULT)
		self.selection_theme = gc(COLOR_SELECTION)
		self.line_number_theme = gc(COLOR_LINENUMBER)
		self.highlighted_line_number_theme = gc(COLOR_HIGHLIGHTED_LINENUMBER)
		self.keyword_theme = gc(COLOR_KEYWORD)
		self.string_theme = gc(COLOR_STRING)
		self.comment_theme = gc(COLOR_COMMENT)

	# set programming-language comment symbol
	def set_comment_symbol(self, single_line_comment, multiline_comment_start, multiline_comment_end):
		self.single_line_comment = single_line_comment
		self.multiline_comment_start = multiline_comment_start
		self.multiline_comment_end = multiline_comment_end

	# when key-press detected
	def perform_action(self, ch):
		self.focus()

		if(ch == -1):
			self.repaint()
			return None
		
		if(ch == curses.KEY_BACKSPACE):
			self.keyHandler.handle_backspace_key(ch)
		elif(ch == curses.KEY_DC):
			self.keyHandler.handle_delete_key(ch)
		elif(ch in [ curses.KEY_HOME, curses.KEY_END ]):
			self.keyHandler.handle_home_end_keys(ch)
		elif(ch in [ curses.KEY_SHOME, curses.KEY_SEND ]):
			self.keyHandler.handle_shift_home_end_keys(ch)
		elif(ch in [ curses.KEY_LEFT, curses.KEY_RIGHT, curses.KEY_UP, curses.KEY_DOWN ]):
			self.keyHandler.handle_arrow_keys(ch)
		elif(ch in [ curses.KEY_PPAGE, curses.KEY_NPAGE ]):
			self.keyHandler.handle_page_navigation_keys(ch)
		elif(ch in [ curses.KEY_SLEFT, curses.KEY_SRIGHT, curses.KEY_SR, curses.KEY_SF ]):
			self.keyHandler.handle_shift_arrow_keys(ch)
		elif(is_ctrl_arrow(ch, "LEFT") or is_ctrl_arrow(ch, "RIGHT")):
			self.keyHandler.handle_ctrl_arrow_keys(ch)
		elif(is_tab(ch) or ch == curses.KEY_BTAB):
			self.keyHandler.handle_tab_keys(ch)
		elif(is_newline(ch)):
			self.keyHandler.handle_newline(ch)
		elif(str(chr(ch)) in self.charset):
			self.keyHandler.handle_printable_character(ch)
		elif(is_ctrl_or_func(ch)):
			self.keyHandler.handle_ctrl_and_func_keys(ch)
		else:
			beep()
		
		self.repaint()

	# returns the vertical portion of the editor to be displayed
	def determine_vertical_visibility(self):
		if(self.curpos.y < self.line_start):
			delta = abs(self.line_start - self.curpos.y)
			self.line_start -= delta
			self.line_end -= delta
		elif(self.curpos.y >= self.line_end):
			delta = abs(self.curpos.y - self.line_end)
			self.line_end += delta + 1
			self.line_start += delta + 1
		return(self.curpos.y - self.line_start)

	# returns the horizontal portion of the editor to be displayed
	def determine_horizontal_visibility(self):
		ctab = (self.tab_size - 1) * self.lines[self.curpos.y][0:self.curpos.x].count("\t")
		curpos_col = self.curpos.x + ctab		# visible cursor position w.r.t. whitespaces

		if(curpos_col < self.col_start):
			delta = abs(self.col_start - curpos_col)
			self.col_start -= delta
			self.col_end -= delta
		elif(curpos_col >= self.col_end):
			delta = abs(curpos_col - self.col_end)
			self.col_end += delta + 1
			self.col_start += delta + 1
		
		# the following ensures when deleting characters, atleast 1 character back is visible
		if(self.col_start > 0 and self.col_start == len(self.lines[self.curpos.y])):
			self.col_start -= 1
			self.col_end -= 1

		return curpos_col - self.col_start		# visible curpos position w.r.t. screen
	
	
	# print selected text using selection-theme
	def print_selection(self, line_index):
		start, end = self.get_selection_endpoints()
		text = self.lines[line_index]
		wstext = text.replace("\t", " " * self.tab_size)
		vtext = wstext[self.col_start:] if self.col_end > len(wstext) else wstext[self.col_start:self.col_end]

		if(start.y == end.y):
			vstartx = start.x + (text[0:start.x].count("\t") * (self.tab_size - 1))
			vendx = end.x + (text[0:end.x].count("\t") * (self.tab_size - 1))
						
			# print in 3 parts: before start, between start & end, after end
			self.parent.addstr(self.y + line_index - self.line_start, self.x + self.line_number_width + 1, vtext[0:vstartx], self.text_theme)
			self.parent.addstr(self.y + line_index - self.line_start, self.x + self.line_number_width + 1 + vstartx, vtext[vstartx:vendx], self.selection_theme)
			self.parent.addstr(self.y + line_index - self.line_start, self.x + self.line_number_width + 1 + vendx, vtext[vendx:], self.text_theme)
		elif(line_index == start.y):
			vstartx = start.x + (text[0:start.x].count("\t") * (self.tab_size - 1))
			
			# print in 2 parts: before start, after start
			self.parent.addstr(self.y + line_index - self.line_start, self.x + self.line_number_width + 1, vtext[0:vstartx], self.text_theme)
			self.parent.addstr(self.y + line_index - self.line_start, self.x + self.line_number_width + 1 + vstartx, vtext[vstartx:], self.selection_theme)
		elif(line_index == end.y):
			vendx = end.x + (text[0:end.x].count("\t") * (self.tab_size - 1))
						
			# print in 2 parts: before end, after end
			self.parent.addstr(self.y + line_index - self.line_start, self.x + self.line_number_width + 1, vtext[0:vendx], self.selection_theme)
			self.parent.addstr(self.y + line_index - self.line_start, self.x + self.line_number_width + 1 + vendx, vtext[vendx:], self.text_theme)
		else:
			self.parent.addstr(self.y + line_index - self.line_start, self.x + self.line_number_width + 1, vtext, self.selection_theme)

	# the primary draw routine for the editor
	def repaint(self):
		curses.curs_set(self.is_in_focus)

		curpos_row = self.determine_vertical_visibility()
		curpos_col = self.determine_horizontal_visibility()
		nlines = len(self.lines)

		for i in range(self.line_start, self.line_end):
			if(i >= nlines): break

			# print line number
			self.parent.addstr(self.y + i - self.line_start, self.x, pad_left_str(str(i+1), self.line_number_width), self.highlighted_line_number_theme if self.curpos.y == i else self.line_number_theme)
			
			# print the text
			text = self.lines[i].replace("\t", " " * self.tab_size)
			if(self.col_start < len(text)):
				vtext = text[self.col_start:] if self.col_end > len(text) else text[self.col_start:self.col_end]
				
				if(self.is_in_selection(i)):
					self.print_selection(i)
				else:
					self.parent.addstr(self.y + i - self.line_start, self.x + self.line_number_width + 1, vtext, self.text_theme)
		
		# reposition the cursor
		try:
			self.parent.move(self.y + curpos_row, self.x + self.line_number_width + 1 + curpos_col)
		except:
			pass
	
	# <---------------------------- Data and File I/O ----------------------------->

	# returns the string representation of the document
	def __str__(self):
		data = ""
		for line in self.lines:
			data += self.newline + line
		return data[len(self.newline):]

	def get_data(self):
		return({
			"text": self.__str__(),
			"curpos": self.curpos,
			"selection_mode": self.selection_mode,
			"sel_start": self.sel_start,
			"sel_end": self.sel_end,
			"filename": self.filename,
			"has_been_allotted_file": self.has_been_allotted_file,
			"save_status": self.save_status
		})

	def set_data(self, data):
		text = data.get("text")
		self.curpos = data.get("curpos")
		self.selection_mode = data.get("selection_mode")
		self.sel_start = data.get("sel_start")
		self.sel_end = data.get("sel_end")
		self.filename = data.get("filename")
		self.has_been_allotted_file = data.get("has_been_allotted_file")
		self.save_status = data.get("save_status")

		self.lines.clear()
		lines = text.splitlines()
		for line in lines:
			self.lines.append(line)

		self.repaint()

	# allots a file and writes to it
	def allot_and_save_file(self, filename):
		self.filename = filename
		self.has_been_allotted_file = True
		try:
			self.save_to_file()
			self.save_status = True
		except:
			self.filename = None
			self.has_been_allotted_file = False
			raise

	# allots a file and reads from it
	def allot_and_open_file(self, filename):
		self.filename = filename
		self.has_been_allotted_file = True
		if(os.path.isfile(self.filename)): self.read_from_file()
		self.save_status = True
		self.parent.update_status()

	# saves data to a file, overwrites it if it exists
	def save_to_file(self):
		data = self.__str__()
		textFile = open(self.filename, "wt")
		textFile.write(data)
		textFile.close()
		self.save_status = True
		self.parent.update_status()

	# saves data to a file, overwrites it if it exists
	def read_from_file(self):
		textFile = open(self.filename, "rt")
		text = textFile.read()
		textFile.close()

		self.selection_mode = False
		self.lines.clear()
		lines = text.splitlines()

		for line in lines:
			self.lines.append(line)

		self.curpos.y = 0
		self.curpos.x = 0

		self.save_status = False
		self.parent.update_status()

	# <--------------------- stub functions ---------------------->

	# delete the selected text
	def delete_selected_text(self):
		return self.utility.delete_selected_text()
	
	# returns the selected text
	def get_selected_text(self):
		return self.utility.get_selected_text()

	# increase indent of selected lines
	def shift_selection_right(self):
		self.utility.shift_selection_right()

	# decrease indent of selected lines
	def shift_selection_left(self):
		self.utility.shift_selection_left()	
	
	# returns the block of leading whitespaces on a given line 
	def get_leading_whitespaces(self, line_index):
		return self.utility.get_leading_whitespaces(line_index)
	
	# checks if line_index is within the text that was selected
	def is_in_selection(self, line_index):
		return self.utility.is_in_selection(line_index)

	# returns the selection endpoints in the correct order
	def get_selection_endpoints(self):
		return self.utility.get_selection_endpoints()

	# implements search
	def find(self, str):
		self.utility.find(str)

	# replaces the first occurrence (after last find/replace operation)
	def find_and_replace(self, strf, strr):
		self.utility.replace(strf, strr)

	# count lines and SLOC
	def get_loc(self):
		return self.utility.get_loc()

	# get file size
	def get_file_size(self):
		return self.utility.get_file_size()