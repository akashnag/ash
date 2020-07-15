# ---------------------------------------------------------------------------------------------
#  Copyright (c) Akash Nag. All rights reserved.
#  Licensed under the MIT License. See LICENSE.md in the project root for license information.
# ---------------------------------------------------------------------------------------------

# This module implements the text-editor widget

from ash.gui import *
from ash.gui.editorKeyHandler import *
from ash.gui.editorUtility import *
from ash.gui.cursorPosition import *
from ash.core.editHistory import *

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
		self.curpos = CursorPosition(0,0)
		
		# set accepted charset
		self.separators = "~`!@#$%^&*()-_=+\\|[{]};:\'\",<.>/? "
		self.charset = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789"
		self.charset += self.separators
		
		# set initial selection status
		self.selection_mode = False
		self.sel_start = CursorPosition(0,0)
		self.sel_end = CursorPosition(0,0)
		self.highlighted_text = None
		self.find_mode = False
		
		# set default tab size
		self.tab_size = 4

		# set wrap options
		self.word_wrap = False
		self.hard_wrap = False
		
		# set up default color themes
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
		self.bid = -1
		self.buffer = None
		
	def reset(self):
		self.selection_mode = False
		self.col_start = 0
		self.col_end = self.width
		self.line_start = 0
		self.line_end = self.height
		self.curpos.x = 0
		self.curpos.y = 0

	def set_buffer(self, bid, buffer):
		self.bid = bid
		self.buffer = buffer
		self.buffer.attach_editor(self)
		self.reset()
		self.notify_self_update()

	def destroy(self):			# called by TopLevelWindow.close_active_editor()
		self.buffer.detach_editor(self)

	def set_wrap(self, word_wrap, hard_wrap):
		self.word_wrap = word_wrap
		self.hard_wrap = hard_wrap	
		self.reset()
		self.notify_self_update()
		self.repaint()

	def wrap_all(self):
		self.sub_lines = list()
		self.cum_sub_line_lengths = list()
		self.grouped_colspans = dict()
		self.col_spans = list()
		self.unexpanded_lines = list()

		if(self.buffer == None): return
		
		total = 0
		for line_index, line in enumerate(self.buffer.lines):
			eline = line.expandtabs(self.tab_size)
			wline = self.utility.wrapped(line, self.width, self.word_wrap, self.hard_wrap)
			ewline = self.utility.wrapped(eline, self.width, self.word_wrap, self.hard_wrap)

			self.unexpanded_lines.extend(wline)

			cumx = 0
			colspan_list = list()
			for sl in wline:
				colspan_list.append( (cumx, cumx + len(sl)-1) )
				cumx += len(sl)

			self.col_spans.extend(colspan_list)
			self.grouped_colspans[line_index] = list(colspan_list)
			self.sub_lines.extend(ewline)
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

	# when focus received
	def focus(self):
		curses.curs_set(False)
		self.is_in_focus = True
		self.repaint()

	# when focus lost
	def blur(self):
		self.is_in_focus = False
		self.repaint()

	# returns the current cursor position
	def get_cursor_position(self):
		return str(self.curpos)

	# set programming-language comment symbol
	def set_comment_symbol(self, single_line_comment, multiline_comment_start, multiline_comment_end):
		self.single_line_comment = single_line_comment
		self.multiline_comment_start = multiline_comment_start
		self.multiline_comment_end = multiline_comment_end

	# when key-press detected
	def perform_action(self, ch):
		if(ch == -1): return None
		if(not self.is_in_focus): self.focus()

		edit_made = False

		if(ch == curses.KEY_BACKSPACE):
			edit_made = self.keyHandler.handle_backspace_key(ch)
		elif(ch == curses.KEY_DC):
			edit_made = self.keyHandler.handle_delete_key(ch)
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
			edit_made = self.keyHandler.handle_tab_keys(ch)
		elif(is_newline(ch)):
			edit_made = self.keyHandler.handle_newline(ch)
		elif(str(chr(ch)) in self.charset):
			edit_made = self.keyHandler.handle_printable_character(ch)
		elif(is_ctrl_or_func(ch)):
			edit_made = self.keyHandler.handle_ctrl_and_func_keys(ch)
		else:
			beep()
		
		if(edit_made): 
			self.buffer.update(self.curpos, self)
			self.notify_self_update()

	# <------------------- Functions called from BufferManager --------------------->

	def notify_update(self):
		if(self.curpos.y >= len(self.buffer.lines) or self.curpos.x > len(self.buffer.lines[self.curpos.y])):
			self.curpos.x = 0
			self.curpos.y = 0			
		if(self.selection_mode):
			if(self.sel_start.y >= len(self.buffer.lines) or self.sel_start.x > len(self.buffer.lines[self.sel_start.y]) or self.sel_end.y >= len(self.buffer.lines) or self.sel_end.x > len(self.buffer.lines[self.sel_end.y])):
				self.selection_mode = False
		
		self.notify_self_update()
		self.repaint()

	def notify_merge(self, new_bid, new_buffer):
		self.bid = new_bid
		self.buffer = new_buffer
		self.selection_mode = False
		if(self.curpos.y >= len(self.buffer.lines) or self.curpos.x > len(self.buffer.lines[self.curpos.y])):
			self.curpos.x = 0
			self.curpos.y = 0
		self.repaint()

	def notify_self_update(self):
		if(self.word_wrap):
			self.wrap_all()
		else:
			self.expanded_lines = expand_tabs_in_lines(self.buffer.lines, self.tab_size)

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
	def print_selection(self, line_index, format = None):
		start, end = self.get_selection_endpoints_rendered()
		
		text = self.unexpanded_lines[line_index]
		wstext = self.rendered_lines[line_index]
		vtext = wstext[self.col_start:] if self.col_end > len(wstext) else wstext[self.col_start:self.col_end]
		
		vstartx = get_horizontal_cursor_position(text, start.x, self.tab_size)
		vendx = get_horizontal_cursor_position(text, end.x, self.tab_size)

		offset_y = self.y + line_index - self.line_start
		offset_x = self.x + self.line_number_width + 1
		
		if(line_index == start.y):
			if(start.y == end.y):
				self.print_formatted(line_index, vtext, format=format)
				self.parent.addstr(offset_y, offset_x + vstartx, vtext[vstartx:vendx], gc("selection"))
			else:
				self.print_formatted(line_index, vtext, format=format)
				self.parent.addstr(offset_y, offset_x + vstartx, vtext[vstartx:], gc("selection"))
		elif(line_index == end.y):
			self.print_formatted(line_index, vtext, format=format)
			self.parent.addstr(offset_y, offset_x, vtext[0:vendx], gc("selection"))			
		else:
			self.parent.addstr(offset_y, offset_x, vtext, gc("selection"))
				
		if(offset_y == self.vcurpos[0] and self.vcurpos[1] >= offset_x and self.vcurpos[1] <= offset_x + len(vtext)):
			char_pos = self.vcurpos[1] - offset_x
			if(char_pos >= len(vtext)):
				char_under_cursor = " "
			else:
				char_under_cursor = vtext[char_pos]
			
			self.parent.addstr(offset_y, self.vcurpos[1], char_under_cursor, gc("cursor") if self.is_in_focus else gc())
			

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
		
		# check conditions where no repaint is necessary
		if(self.height <= 0 or self.width <= 0): return
		if(self.curpos.x < 0 or self.curpos.y < 0): return
		if(self.line_start < 0 or self.line_end <= self.line_start): return
		if(self.col_start < 0 or self.col_end <= self.col_start): return
		if(self.buffer == None): return
				
		# get the data to be displayed after performing tab-expansion and word-wrapping
		if(self.word_wrap):
			self.rendered_lines = self.sub_lines
			self.rendered_curpos = self.utility.get_rendered_pos(self.curpos)
			if(self.selection_mode):
				self.rendered_sel_start = self.utility.get_rendered_pos(self.sel_start)
				self.rendered_sel_end = self.utility.get_rendered_pos(self.sel_end)
		else:
			self.unexpanded_lines = self.buffer.lines
			self.rendered_lines = self.expanded_lines
			rcx = get_horizontal_cursor_position(self.buffer.lines[self.curpos.y], self.curpos.x, self.tab_size)
			self.rendered_curpos = CursorPosition(self.curpos.y, rcx)
			self.rendered_sel_start = self.sel_start
			self.rendered_sel_end = self.sel_end

		# determine the cursor position to be displayed w.r.t the screen
		nlines = len(self.rendered_lines)
		curpos_row = self.determine_vertical_visibility()
		curpos_col = self.determine_horizontal_visibility()
		self.vcurpos = (self.y + curpos_row, self.x + self.line_number_width + 1 + curpos_col)
		
		# set up location of text-highlights
		if(self.selection_mode and not self.find_mode):
			start, end = self.get_selection_endpoints_rendered()
			if(start.y == end.y):
				text = self.unexpanded_lines[start.y]
				wstext = self.rendered_lines[start.y]
				vtext = wstext[self.col_start:] if self.col_end > len(wstext) else wstext[self.col_start:self.col_end]
				vstartx = get_horizontal_cursor_position(text, start.x, self.tab_size)
				vendx = get_horizontal_cursor_position(text, end.x, self.tab_size)
				self.highlighted_text = vtext[vstartx:vendx]
			else:
				self.highlighted_text = None
		elif(not self.find_mode):
			self.highlighted_text = None

		last_line_number_printed = 0

		# get syntax highlighting for all lines in the range to be displayed
		line_formats = get_format_list_for_lines(self.buffer, self.rendered_lines, self.line_start, self.line_end, nlines)

		for i in range(self.line_start, self.line_end):
			if(i >= nlines): break

			# compute whether line-number should be highlighted
			if(self.show_line_numbers):
				if(self.word_wrap):
					line_number = translate_line_number(i, self.cum_sub_line_lengths) 
					if(len(line_number) > 0): last_line_number_printed = int(line_number)
					
					if(should_highlight(self.rendered_curpos.y, i, self.cum_sub_line_lengths, last_line_number_printed)):
						line_theme = gc("highlighted-line-number")
					else:
						line_theme = gc("line-number")
				else:
					line_number = str(i + 1)				
					line_theme = gc("highlighted-line-number") if self.rendered_curpos.y == i else gc("line-number")
				
				# print the line number
				self.parent.addstr(self.y + i - self.line_start, self.x, line_number.rjust(self.line_number_width), line_theme)
			
			# get the line to be printed
			text = self.rendered_lines[i]
			
			# calculate the portion of the line to be actually displayed on screen
			cs = self.col_start			
			if(self.col_end > len(text)):
				vtext = text[self.col_start:]
				ce = len(text)
			else:
				vtext = text[self.col_start:self.col_end]
				ce = self.col_end

			# get the portion of syntax highlighting necessary to display the visible portion of the line
			partial_format = get_sub_lex_list(line_formats[i-self.line_start], cs, ce)
			
			# print either in selection mode or normal syntax-highlighted mode
			if(self.is_in_selection_rendered(i)):
				self.print_selection(i, format=partial_format)
			else:
				self.print_formatted(i, vtext, format=partial_format)

	def get_real_line_from_rendered_line(self, rline):
		if(not self.word_wrap): return rline
		index = approx_bsearch(self.cum_sub_line_lengths, rline)
		
		if(rline < self.cum_sub_line_lengths[index]): index -= 1
		return index
		
	def print_formatted(self, i, vtext, off_y = 0, off_x = 0, format = None):
		offset_y = self.y + i - self.line_start + off_y
		init_offset_x = self.x + self.line_number_width + 1 + off_x
		offset_x = init_offset_x
		char_under_cursor = None
		
		if(format == None): format = self.buffer.format_code(vtext)
		n = len(format)
		for i in range(n):
			index, style, text = format[i]
			tlen = len(text)
			self.parent.addstr(offset_y, offset_x, text, style)
				
			if(offset_y == self.vcurpos[0] and self.vcurpos[1] >= offset_x and self.vcurpos[1] <= offset_x + len(text)):
				char_pos = self.vcurpos[1] - offset_x
				if(char_pos >= len(text)):
					char_under_cursor = " "
				else:
					char_under_cursor = text[char_pos]
					
			offset_x += tlen
			
		
		self.highlight(offset_y, init_offset_x, vtext)

		if(char_under_cursor != None):			
			self.parent.addstr(offset_y, self.vcurpos[1], char_under_cursor, gc("cursor") if self.is_in_focus else gc())
		else:
			if(offset_y == self.vcurpos[0] and n==0):
				self.parent.addstr(offset_y, self.vcurpos[1], " ", gc("cursor") if self.is_in_focus else gc())


	def highlight(self, offset_y, offset_x, vtext):
		if(self.highlighted_text == None): return
		
		pos = -1
		while(True):
			pos = vtext.find(self.highlighted_text, pos + 1)
			if(pos < 0): return
			n = len(self.highlighted_text)
			self.parent.addstr(offset_y, offset_x + pos, self.highlighted_text, gc("highlight"))

	# <-------------------------------------------------------------------------------------->

	# <---------------------------- Data and File I/O ----------------------------->

	# returns the selection length (for incorporating into status-bar)
	def get_selection_length_as_string(self):
		if(not self.selection_mode): return ""
		
		count = 0
		start, end = self.get_selection_endpoints()

		if(start.y != end.y):
			for i in range(start.y + 1, end.y):
				count += len(self.buffer.lines[i]) + 1

			count += len(self.buffer.lines[start.y]) - start.x
			count += end.x
			count += 1
		else:
			count = end.x - start.x

		return " {" + str(count) + "}"

	# returns the string representation of the document
	def __str__(self):
		return self.buffer.get_data()

	# returns information about editor-state
	def get_info(self):
		return({
			"bid": self.bid,
			"buffer": self.buffer,
			"selection_mode": self.selection_mode,
			"sel_start": self.sel_start,
			"sel_end": self.sel_end,
			"tab_size": self.tab_size
		})		

	# turns on/off line numbers
	def toggle_line_numbers(self, show_numbers):
		self.show_line_numbers = show_numbers
		if(self.show_line_numbers):
			self.line_number_width = PREFERRED_LINE_NUMBER_WIDTH
		else:
			self.line_number_width = 0
		self.repaint()

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

	# returns the block of leading whitespaces on a given rendered line
	def get_leading_whitespaces_rendered(self, line_index):
		return self.utility.get_leading_whitespaces_rendered(line_index)
		
	# returns the selection endpoints in the correct order
	def get_selection_endpoints(self):
		return self.utility.get_selection_endpoints()

	# get file size
	def get_file_size(self):
		return self.utility.get_file_size()

	# highlights all instances
	def find_all(self, search_text):
		self.utility.find_all(search_text)
		self.repaint()

	# cancels the find mode
	def cancel_find(self):
		self.utility.cancel_find()
		self.repaint()

	# find next match
	def find_next(self, search_text):
		self.utility.find_next(search_text)
		self.parent.repaint()
		
	# find previous match
	def find_previous(self, search_text):
		self.utility.find_previous(search_text)
		self.parent.repaint()
		
	# replace next instance
	def replace_next(self, search_text, replace_text):
		self.utility.replace_next(search_text, replace_text)
		self.parent.repaint()
		
	# replace all instances
	def replace_all(self, search_text, replace_text):
		self.utility.replace_all(search_text, replace_text)
		self.parent.repaint()