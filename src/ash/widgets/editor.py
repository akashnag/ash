# ---------------------------------------------------------------------------------------------
#  Copyright (c) Akash Nag. All rights reserved.
#  Licensed under the MIT License. See LICENSE.md in the project root for license information.
# ---------------------------------------------------------------------------------------------

# This module implements the text-editor widget

from ash.widgets import *
from ash.widgets.editorKeyHandler import *
from ash.widgets.editorUtility import *

PREFERRED_LINE_NUMBER_WIDTH = 6

# This is the text editor class
class Editor(Widget):
	def __init__(self, parent):
		super().__init__(WIDGET_TYPE_EDITOR, True, True)
		
		# initialize parent window
		self.parent = parent

		# initialize helper classes
		self.utility = EditorUtility(self)
		self.keyHandler = EditorKeyHandler(self)
				
		self.line_number_width = PREFERRED_LINE_NUMBER_WIDTH
		self.show_line_numbers = True
		self.word_wrap = False
						
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
		self.encoding = "utf-8"

		# set default tab size
		self.tab_size = 4

		# set wrap options
		self.word_wrap = False
		self.hard_wrap = False
		
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
		self.history = None
	
	def set_wrap(self, word_wrap, hard_wrap):
		self.word_wrap = word_wrap
		self.hard_wrap = hard_wrap
		self.selection_mode = False
		self.col_start = 0
		self.col_end = self.width
		self.line_start = 0
		self.line_end = self.height
		self.curpos.x = 0
		self.curpos.y = 0
		self.repaint()

	def wrap_all(self):
		self.sub_lines = list()
		self.cum_sub_line_lengths = list()
		total = 0
		for line in self.lines:
			wline = wrapped(line, self.width, self.word_wrap, self.hard_wrap)
			self.sub_lines.extend(wline)
			self.cum_sub_line_lengths.append(total)
			total += len(wline)
		self.cum_sub_line_lengths.append(total)

	# resize editor
	def resize(self, y, x, height, width, forced=False):
		if(not forced and height == self.height and width == self.full_width): return

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

		self.repaint()

	# checks to see if editor can be closed without user confirmation
	def can_quit(self):
		if(self.save_status): return True
		if(not self.has_been_allotted_file and len(self.__str__()) == 0): return True
		return False

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
		
		if(self.history == None): self.history = EditHistory(self.__str__(), self.curpos)
		
		undoable_action = False

		if(ch == curses.KEY_BACKSPACE):
			undoable_action = self.keyHandler.handle_backspace_key(ch)
		elif(ch == curses.KEY_DC):
			undoable_action = self.keyHandler.handle_delete_key(ch)
		elif(ch in [ curses.KEY_HOME, curses.KEY_END ]):
			self.keyHandler.handle_home_end_keys(ch)
		elif(ch in [ curses.KEY_SHOME, curses.KEY_SEND ]):
			self.keyHandler.handle_shift_home_end_keys(ch)
		elif(is_keyname(ch, "HOM5") or is_keyname(ch, "END5")):
			self.keyHandler.handle_ctrl_home_end_keys(ch)
		elif(ch in [ curses.KEY_LEFT, curses.KEY_RIGHT, curses.KEY_UP, curses.KEY_DOWN ]):
			self.keyHandler.handle_arrow_keys(ch)
		elif(ch in [ curses.KEY_PPAGE, curses.KEY_NPAGE ]):
			self.keyHandler.handle_page_navigation_keys(ch)
		elif(ch in [ curses.KEY_SPREVIOUS, curses.KEY_SNEXT ]):
			self.keyHandler.handle_shift_page_navigation_keys(ch)
		elif(ch in [ curses.KEY_SLEFT, curses.KEY_SRIGHT, curses.KEY_SR, curses.KEY_SF ]):
			self.keyHandler.handle_shift_arrow_keys(ch)
		elif(is_ctrl_arrow(ch, "LEFT") or is_ctrl_arrow(ch, "RIGHT")):
			self.keyHandler.handle_ctrl_arrow_keys(ch)
		elif(is_tab(ch) or ch == curses.KEY_BTAB):
			undoable_action = self.keyHandler.handle_tab_keys(ch)
		elif(is_newline(ch)):
			undoable_action = self.keyHandler.handle_newline(ch)
		elif(str(chr(ch)) in self.charset):
			undoable_action = self.keyHandler.handle_printable_character(ch)
		elif(is_ctrl_or_func(ch)):
			undoable_action = self.keyHandler.handle_ctrl_and_func_keys(ch)
		else:
			beep()
		
		if(undoable_action):
			self.history.add_change(self.__str__(), self.curpos)

		self.repaint()


	# <---------------------------- Repaint Operations ----------------------------->

		# checks if line_index is within the text that was selected
	def is_in_selection_rendered(self, line_index):
		if(self.selection_mode):
			if(is_start_before_end(self.rendered_sel_start, self.rendered_sel_end)):
				return(True if (line_index >= self.rendered_sel_start.y and line_index <= self.rendered_sel_end.y) else False)
			else:
				return(True if (line_index >= self.rendered_sel_end.y and line_index <= self.rendered_sel_start.y) else False)
		else:
			return False

	# returns the selection endpoints in the correct order
	def get_selection_endpoints_rendered(self):
		forward_sel = is_start_before_end(self.rendered_sel_start, self.rendered_sel_end)
		if(forward_sel):
			start = copy.copy(self.rendered_sel_start)
			end = copy.copy(self.rendered_sel_end)
		else:
			start = copy.copy(self.rendered_sel_end)
			end = copy.copy(self.rendered_sel_start)
		return (start, end)

	# print selected text using selection-theme
	def print_selection(self, line_index):
		start, end = self.get_selection_endpoints_rendered()
		
		text = self.rendered_lines[line_index]
		wstext = text.expandtabs(self.tab_size)
		vtext = wstext[self.col_start:] if self.col_end > len(wstext) else wstext[self.col_start:self.col_end]
		
		vstartx = get_horizontal_cursor_position(text, start.x, self.tab_size)
		vendx = get_horizontal_cursor_position(text, end.x, self.tab_size)

		if(start.y == end.y):						
			# print in 3 parts: before start, between start & end, after end
			self.parent.addstr(self.y + line_index - self.line_start, self.x + self.line_number_width + 1, vtext[0:vstartx], self.text_theme)
			self.parent.addstr(self.y + line_index - self.line_start, self.x + self.line_number_width + 1 + vstartx, vtext[vstartx:vendx], self.selection_theme)
			self.parent.addstr(self.y + line_index - self.line_start, self.x + self.line_number_width + 1 + vendx, vtext[vendx:], self.text_theme)
		elif(line_index == start.y):
			# print in 2 parts: before start, after start
			self.parent.addstr(self.y + line_index - self.line_start, self.x + self.line_number_width + 1, vtext[0:vstartx], self.text_theme)
			self.parent.addstr(self.y + line_index - self.line_start, self.x + self.line_number_width + 1 + vstartx, vtext[vstartx:], self.selection_theme)
		elif(line_index == end.y):
			# print in 2 parts: before end, after end
			self.parent.addstr(self.y + line_index - self.line_start, self.x + self.line_number_width + 1, vtext[0:vendx], self.selection_theme)
			self.parent.addstr(self.y + line_index - self.line_start, self.x + self.line_number_width + 1 + vendx, vtext[vendx:], self.text_theme)
		else:
			self.parent.addstr(self.y + line_index - self.line_start, self.x + self.line_number_width + 1, vtext, self.selection_theme)

	# returns the vertical portion of the editor to be displayed
	def determine_vertical_visibility(self):
		if(self.rendered_curpos.y < self.line_start):
			delta = abs(self.line_start - self.rendered_curpos.y)
			self.line_start -= delta
			self.line_end -= delta
		elif(self.rendered_curpos.y >= self.line_end):
			delta = abs(self.rendered_curpos.y - self.line_end)
			self.line_end += delta + 1
			self.line_start += delta + 1
		return(self.rendered_curpos.y - self.line_start)

	# returns the horizontal portion of the editor to be displayed
	def determine_horizontal_visibility(self):
		curpos_col = get_horizontal_cursor_position(self.rendered_lines[self.rendered_curpos.y], self.rendered_curpos.x, self.tab_size)
		
		if(curpos_col < self.col_start):
			delta = abs(self.col_start - curpos_col)
			self.col_start -= delta
			self.col_end -= delta
		elif(curpos_col >= self.col_end):
			delta = abs(curpos_col - self.col_end)
			self.col_end += delta + 1
			self.col_start += delta + 1
		
		# the following ensures when deleting characters, atleast 1 character back is visible
		if(self.col_start > 0 and self.col_start == len(self.rendered_lines[self.rendered_curpos.y])):
			self.col_start -= 1
			self.col_end -= 1

		return curpos_col - self.col_start		# visible curpos position w.r.t. screen
	
	# the primary draw routine for the editor
	def repaint(self):
		self.parent.layout_manager.readjust()

		if(self.height <= 0 or self.width <= 0): return
		if(self.curpos.x < 0 or self.curpos.y < 0 or self.line_start < 0 or self.line_end <= self.line_start or self.col_start < 0 or self.col_end <= self.col_start): return

		curses.curs_set(self.is_in_focus)

		if(self.word_wrap):
			self.wrap_all()
			self.rendered_lines = self.sub_lines
			self.rendered_curpos = get_rendered_pos(self.lines, self.width, self.hard_wrap, self.curpos, self.cum_sub_line_lengths)

			if(self.selection_mode):
				self.rendered_sel_start = get_rendered_pos(self.lines, self.width, self.hard_wrap, self.sel_start, self.cum_sub_line_lengths)
				self.rendered_sel_end = get_rendered_pos(self.lines, self.width, self.hard_wrap, self.sel_end, self.cum_sub_line_lengths)
		else:
			self.rendered_lines = self.lines
			self.rendered_curpos = self.curpos
			self.rendered_sel_start = self.sel_start
			self.rendered_sel_end = self.sel_end

		curpos_row = self.determine_vertical_visibility()
		curpos_col = self.determine_horizontal_visibility()
		nlines = len(self.rendered_lines)
		
		last_line_number_printed = 0
		for i in range(self.line_start, self.line_end):
			if(i >= nlines): break

			# print line number
			if(self.show_line_numbers):
				if(self.word_wrap):
					line_number = translate_line_number(i, self.cum_sub_line_lengths) 
					if(len(line_number) > 0): last_line_number_printed = int(line_number)
					
					if(should_highlight(self.rendered_curpos.y, i, self.cum_sub_line_lengths, last_line_number_printed)):
						line_theme = self.highlighted_line_number_theme
					else:
						line_theme = self.line_number_theme
				else:
					line_number = str(i + 1)				
					line_theme = self.highlighted_line_number_theme if self.rendered_curpos.y == i else self.line_number_theme
				
				self.parent.addstr(self.y + i - self.line_start, self.x, line_number.rjust(self.line_number_width), line_theme)
			
			# print the text
			text = self.rendered_lines[i].expandtabs(self.tab_size)

			if(self.col_start < len(text)):
				vtext = text[self.col_start:] if self.col_end > len(text) else text[self.col_start:self.col_end]
				
				if(self.is_in_selection_rendered(i)):
					self.print_selection(i)
				else:
					self.parent.addstr(self.y + i - self.line_start, self.x + self.line_number_width + 1, vtext, self.text_theme)
		
		# reposition the cursor
		try:
			if(self.is_in_focus): self.parent.move(self.y + curpos_row, self.x + self.line_number_width + 1 + curpos_col)
		except:
			self.parent.addstr(0,0,str(self.y + curpos_row)+","+str(self.x + self.line_number_width + 1 + curpos_col),gc())
		
	# <-------------------------------------------------------------------------------------->

	# <---------------------------- Data and File I/O ----------------------------->

	# returns the selection length (for incorporating into status-bar)
	def get_selection_length_as_string(self):
		if(not self.selection_mode): return ""
		
		count = 0
		start, end = self.get_selection_endpoints()

		if(start.y != end.y):
			for i in range(start.y + 1, end.y):
				count += len(self.lines[i]) + 1

			count += len(self.lines[start.y]) - start.x
			count += end.x
			count += 1
		else:
			count = end.x - start.x

		return " {" + str(count) + "}"

	# returns the string representation of the document
	def __str__(self):
		return self.newline.join(self.lines)

	# returns a file-data object
	def get_data(self):
		file_data = FileData(self.filename, self.__str__(), self.curpos, self.save_status, self.selection_mode, self.sel_start, self.sel_end, self.encoding, self.tab_size)
		return file_data

	# assigns a file-data object
	def set_data(self, file_data):
		text = file_data.buffer

		self.curpos = file_data.curpos
		self.selection_mode = file_data.selection_mode
		self.sel_start = file_data.sel_start
		self.sel_end = file_data.sel_end
		self.filename = file_data.filename
		self.has_been_allotted_file = file_data.has_been_allotted_file
		self.save_status = file_data.save_status
		self.encoding = file_data.encoding
		self.tab_size = file_data.tab_size

		self.render_data_to_lines(text)

	def render_data_to_lines(self, text, initialize_history = True):
		# parse lines
		self.lines.clear()
		if(len(text) == 0):
			self.lines.append("")
		else:
			lines = text.splitlines()
			for line in lines:
				self.lines.append(line)
			if(text.endswith("\n")): self.lines.append("")

		# initialize history
		if(initialize_history): self.history = EditHistory(text, CursorPosition(0,0))

	# allots a file and writes to it
	def allot_and_save_file(self, filename):
		self.filename = filename
		self.has_been_allotted_file = True
		try:
			self.save_to_file()
			self.parent.update_status()
		except:
			self.filename = None
			self.has_been_allotted_file = False
			raise

	# save to file
	def save_to_file(self):
		# save to buffer
		save_to_buffer(self.parent.app.files, self, True)
		# write buffer to disk
		write_buffer_to_disk(self.parent.app.files, self.filename)
		# update status
		self.save_status = True
	
	# saves data to a file, overwrites it if it exists
	def read_from_file(self):
		text = load_buffer_from_disk(self.parent.app.files, self.filename)
		
		self.selection_mode = False
		self.render_data_to_lines(text)
		self.curpos.y = 0
		self.curpos.x = 0

		self.save_status = True
		self.parent.update_status()

	# checks if no data
	def is_empty(self):
		return True if len(self.__str__())==0 else False

	# turns on/off line numbers
	def toggle_line_numbers(self, show_numbers):
		self.show_line_numbers = show_numbers
		if(self.show_line_numbers):
			self.line_number_width = PREFERRED_LINE_NUMBER_WIDTH
		else:
			self.line_number_width = 0
		self.repaint()

	# turns on/off soft-wrap
	def toggle_word_wrap(self, wrap):
		pass		# add code

	# <--------------------- stub functions ---------------------->

	# delete the selected text
	def delete_selected_text(self):
		return self.utility.delete_selected_text()
	
	# returns the selected text
	def get_selected_text(self):
		return self.utility.get_selected_text()

	# increase indent of selected lines
	def shift_selection_right(self):
		return self.utility.shift_selection_right()

	# decrease indent of selected lines
	def shift_selection_left(self):
		return self.utility.shift_selection_left()	
	
	# returns the block of leading whitespaces on a given line 
	def get_leading_whitespaces(self, line_index):
		return self.utility.get_leading_whitespaces(line_index)
	
	# checks if line_index is within the text that was selected
	def is_in_selection(self, line_index):
		return self.utility.is_in_selection(line_index)

	# returns the selection endpoints in the correct order
	def get_selection_endpoints(self):
		return self.utility.get_selection_endpoints()

	# count lines and SLOC
	def get_loc(self):
		return self.utility.get_loc()

	# get file size
	def get_file_size(self):
		return self.utility.get_file_size()