# ---------------------------------------------------------------------------------------------
#  Copyright (c) Akash Nag. All rights reserved.
#  Licensed under the MIT License. See LICENSE.md in the project root for license information.
# ---------------------------------------------------------------------------------------------

# This module handles the screen buffer

from ash.formatting.colors import *
from ash.gui.cursorPosition import *
from ash.utils.utils import *
import datetime

cdef class Screen:
	cdef bint show_line_numbers, show_scrollbars
	cdef int total_rendered_lines
	cdef int height, width
	cdef int line_start, line_end
	cdef int col_start, col_end
	cdef buffer
	cdef win
	cdef dict all_col_spans
	cdef dict mapping_real_line_to_rendered_line
	cdef dict mapping_rendered_line_to_real_line
	cdef list screen_buffer
	cdef list style_buffer
	cdef int real_line_start_index_visible, real_line_end_index_visible
	cdef int last_gutter_width
	cdef int last_tab_size, last_text_area_width
	cdef bint last_word_wrap, last_hard_wrap
	cdef bint supports_colors

	# initialize the screen buffer
	def __init__(self, supports_colors, win, buffer, int height, int width, show_line_numbers, show_scrollbars):
		self.supports_colors = 1 if supports_colors else 0
		self.all_col_spans = None
		self.show_line_numbers = show_line_numbers
		self.show_scrollbars = show_scrollbars
		self.update(win, buffer)
		self.resize(height, width)

	def toggle_line_numbers_and_scrollbars(self, show_ln, show_sb):
		self.show_line_numbers = show_ln
		self.show_scrollbars = show_sb
		self.last_gutter_width = self._get_gutter_width(self.line_end)

	# resize the screen buffer
	def resize(self, int height, int width):
		self.height = height
		self.width = width
		self.line_start = 0
		self.line_end = self.height
		self.col_start = 0
		self.col_end = self.width - self._get_gutter_width(self.line_end)
		self.last_gutter_width = self._get_gutter_width(self.line_end)
		self.clear()

	# update the window and buffer
	def update(self, win, buffer):
		self.win = win
		self.buffer = buffer

	# clear the screen buffer
	cdef clear(self):
		self.screen_buffer = [ " " * self.width for y in range(self.height) ]
		self.style_buffer = [ [ gc("editor-background") for x in range(self.width) ] for y in range(self.height) ]

	# put a string in a position
	cdef putstr(self, int y, int x, s):
		temp = self.screen_buffer[y]
		self.screen_buffer[y] = temp[0:x] + s + temp[x+len(s):]

	# puts the line number in the gutter
	cdef put_line_number(self, int y, int line_number, int gutter_width):
		self.putstr(y, 0, str(line_number).rjust(gutter_width-1))

	# show the fake cursor in the specified location
	cdef put_cursor(self, int y, int x):
		try:
			self.style_buffer[y][x] = gc("cursor") | (0 if(self.supports_colors==1) else curses.A_REVERSE)
		except:
			pass

	# highlight a line
	cdef highlight_line(self, int y, int gutter_width):
		self.set_style(y, 0, gutter_width, gc("highlighted-line-number") | (0 if(self.supports_colors==1) else curses.A_BOLD))

	# set the style of the gutter
	cdef set_gutter_style(self, int gutter_width):
		for y in range(self.height):
			self.set_style(y, 0, gutter_width, gc("line-number"))

	# set the style of a portion in the screen buffer from [x_start = inclusive, x_end = exclusive)
	cdef set_style(self, int y, int x_start, int x_end, style):
		for x in range(x_start, x_end):
			self.style_buffer[y][x] = style

	# set the style of a particular location in the screen buffer
	cdef set_style_single(self, pos, style):
		try:
			self.style_buffer[pos.y][pos.x] = style
			return True
		except:
			return False

	# determine the space to be reserved for the gutter (left, to show line number) = 1 space on either side and linenumber in middle
	cdef _get_gutter_width(self, int line_end):
		if(self.show_line_numbers):
			x = str(line_end)
			return (3 if line_end < 10 else 2) + len(x) + (1 if self.show_scrollbars else 0)
		else:
			return 1 + (1 if self.show_scrollbars else 0)

	# returns a list of indices in a text wherever separators (given in delims) are found
	cdef get_delimiter_positions_list(self, text, delims):
		cdef int i, n
		n = len(text)
		pos = list()
		
		for i in range(n):
			if(text[i] in delims): pos.append(i)
		
		# also add the length of the string (as the last index+1)
		pos.append(n)
		return sorted(pos)

	# reflows a document containing multiple lines depending on wrap settings and after expansion of tabs
	def reflow_all(self, width, lines, tab_size, word_wrap, hard_wrap):
		self.all_col_spans = dict()
		self.mapping_real_line_to_rendered_line = dict()		# only the 1st rendered line
		self.mapping_rendered_line_to_real_line = dict()		# contains tuple(real_line_index, subline_offset)
		
		self.total_rendered_lines = 0
		rendered_counter = 0
		
		for i, line in enumerate(lines):
			self.all_col_spans[i] = self.reflow(width, line, tab_size, word_wrap, hard_wrap)
			self.mapping_real_line_to_rendered_line[i] = rendered_counter
			
			k = len(self.all_col_spans[i])
			for j in range(k):
				self.mapping_rendered_line_to_real_line[rendered_counter+j] = (i,j)

			if(k == 0):
				self.total_rendered_lines += 1
				self.mapping_rendered_line_to_real_line[rendered_counter] = (i,0)
				rendered_counter += 1
			else:
				self.total_rendered_lines += k
				rendered_counter += k

	# reflow a line of text (depending on wrap settings and tab-size) and return a list of column-spans (after tab-expansion)
	cdef reflow(self, int width, line, int tab_size, bint word_wrap, bint hard_wrap):
		text = line.expandtabs(tab_size)
		col_spans = list()
		separators = set(" ,.()[]{}:;\'\"?")
		pos = self.get_delimiter_positions_list(text, separators)
		
		cdef int pos_start = 0
		cdef int len_pos = len(pos)
		cdef int col_start = 0
		cdef int col_end = 0
		cdef int col_width
		cdef int ls, i = 0
		cdef int w = len(text)
		cdef bint flag

		# text wrap is OFF
		if(w == 0): return col_spans
		if(not word_wrap or w <= width): return([ (0, w-1) ])
		
		# hard wrap is ON
		if(hard_wrap):
			ls = w // width					# number of lines to be broken into
			col_width = w % width			# width of the last line
			while(ls > 0):
				col_spans.append( (col_start, col_start + width - 1) )
				col_start += width
				ls -= 1
			if(col_width > 0): col_spans.append( (col_start, col_start + col_width - 1) )
			return col_spans
	
		# soft wrap is ON
		while(col_start < w):
			flag = False
			for i in range(pos_start, len_pos):
				if(pos[i] > col_start + width): 
					flag = True
					break
			
			if(i == pos_start or not flag): i+=1
			
			if(pos[i-1] - col_start < width):
				col_end = pos[i-1]
				col_spans.append( (col_start, col_end) )
				col_start = pos[i-1]+1
			else:
				col_end = pos[i-1]-1
				col_spans.append( (col_start, col_end) )
				col_start = pos[i-1]

			pos_start = i
		
		return col_spans

	cdef _get_line_start(self, int nlines, lines):
		cdef int rendered_line_index = -1
		cdef int i, real_line_start, line_start_offset, j

		for i in range(nlines):
			col_spans = self.all_col_spans[i]
			if(len(col_spans) == 0): 
				rendered_line_index += 1
				if(rendered_line_index == self.line_start):
					real_line_start = i
					line_start_col_spans = col_spans			# col positions are AFTER tab expansion
					line_start_offset = 0
					return (real_line_start, line_start_col_spans, line_start_offset)
			else:
				for j in range(len(col_spans)):
					rendered_line_index += 1
					if(rendered_line_index == self.line_start):
						real_line_start = i
						line_start_col_spans = col_spans			# col positions are AFTER tab expansion
						line_start_offset = j
						return (real_line_start, line_start_col_spans, line_start_offset)
	
	cdef perform_syntax_highlighting(self, lines, int text_area_width, real_curpos, int tab_size, bint word_wrap, bint hard_wrap):
		cdef int start_line_index, end_line_index
		start_line_index, end_line_index = self.real_line_start_index_visible, self.real_line_end_index_visible
		cdef int gutter_width = self.width - text_area_width
		cdef int line_index, visible_line_index

		if(self.buffer.formatter.lexer == None): return

		# cannot use join as it will mess up the lexer indices with the insertion of newline characters
		for line_index in range(start_line_index, end_line_index):
			temp = CursorPosition(line_index, 0)
			visible_line_index = self.mapping_real_line_to_rendered_line[line_index] - 1

			data = lines[line_index]
			# lex-data contains a list of tuples(index, style, text)
			lex_data = self.buffer.format_code(data)
			for style_info in lex_data:
				start_index = style_info[0]
				style = style_info[1]
				text = style_info[2]
				temp.x = start_index
				
				rendered_pos, _ = self.translate_real_curpos_to_rendered_curpos(lines, temp, text_area_width, tab_size, word_wrap, hard_wrap, visible_line_index)
				if(rendered_pos.x >= self.col_end): break

				for index in range(len(text)):
					temp.x = start_index + index
					rendered_pos, _ = self.translate_real_curpos_to_rendered_curpos(lines, temp, text_area_width, tab_size, word_wrap, hard_wrap, visible_line_index)
					if(rendered_pos.x >= self.col_end): continue

					visual_pos = self.translate_rendered_to_visual_pos(rendered_pos, gutter_width)
					self.set_style_single(visual_pos, style)

	cdef is_start_before_end(self, start, end):
		if(start.y == end.y and start.x < end.x): return True
		if(start.y < end.y): return True
		return False

	cdef perform_selection_highlighting(self, lines, int text_area_width, real_curpos, rendered_curpos, int tab_size, bint word_wrap, bint hard_wrap, selection_info):
		sel_start, sel_end = self.get_selection_endpoints(selection_info["start"], selection_info["end"])
		cdef int max_start_x = len(lines[sel_start.y])
		temp = copy.copy(sel_start)
		cdef int gutter_width = self.width - text_area_width
		cdef int y, x
		cdef int visible_line_index = self.get_pre_translation_parameters(lines, temp, text_area_width, tab_size, word_wrap, hard_wrap)
		if(sel_start.y != sel_end.y):
			for x in range(sel_start.x, max_start_x):
				temp.x = x
				rendered_temp, _ = self.translate_real_curpos_to_rendered_curpos(lines, temp, text_area_width, tab_size, word_wrap, hard_wrap, visible_line_index)
				visual = self.translate_rendered_to_visual_pos(rendered_temp, gutter_width)
				self.set_style_single(visual, gc("selection") | (0 if(self.supports_colors==1) else curses.A_REVERSE))
		else:
			for x in range(sel_start.x, sel_end.x):
				temp.x = x
				rendered_temp, _ = self.translate_real_curpos_to_rendered_curpos(lines, temp, text_area_width, tab_size, word_wrap, hard_wrap, visible_line_index)
				visual = self.translate_rendered_to_visual_pos(rendered_temp, gutter_width)
				self.set_style_single(visual, gc("selection") | (0 if(self.supports_colors==1) else curses.A_REVERSE))

		for y in range(sel_start.y + 1, sel_end.y):
			temp.y = y
			visible_line_index = self.get_pre_translation_parameters(lines, temp, text_area_width, tab_size, word_wrap, hard_wrap)
			max_start_x = len(lines[y])
			for x in range(max_start_x):
				temp.x = x
				rendered_temp, _ = self.translate_real_curpos_to_rendered_curpos(lines, temp, text_area_width, tab_size, word_wrap, hard_wrap, visible_line_index)
				visual = self.translate_rendered_to_visual_pos(rendered_temp, gutter_width)
				self.set_style_single(visual, gc("selection") | (0 if(self.supports_colors==1) else curses.A_REVERSE))
		
		if(sel_start.y != sel_end.y):
			temp.y = sel_end.y
			visible_line_index = self.get_pre_translation_parameters(lines, temp, text_area_width, tab_size, word_wrap, hard_wrap)
			for x in range(sel_end.x):
				temp.x = x
				rendered_temp, _ = self.translate_real_curpos_to_rendered_curpos(lines, temp, text_area_width, tab_size, word_wrap, hard_wrap, visible_line_index)
				visual = self.translate_rendered_to_visual_pos(rendered_temp, gutter_width)
				self.set_style_single(visual, gc("selection") | (0 if(self.supports_colors==1) else curses.A_REVERSE))

	cdef translate_rendered_to_visual_pos(self, rendered_pos, int gutter_width):
		if(self.line_start > rendered_pos.y or self.col_start > rendered_pos.x):
			# invisible
			return None
		else:
			return CursorPosition( rendered_pos.y - self.line_start, rendered_pos.x - self.col_start + gutter_width)

	cdef translate_visual_to_rendered_pos(self, visual_pos, int gutter_width):
		cdef int y, x
		y = visual_pos.y + self.line_start + 0			# TODO: +1 or +0: correction: recheck
		x = visual_pos.x + self.col_start - gutter_width
		if(x < 0 or y < 0):
			return None
		else:
			return CursorPosition(y, x)

	cdef perform_search_highlighting(self, lines, int text_area_width, real_curpos, int tab_size, bint word_wrap, bint hard_wrap, highlight_info):
		search_text = highlight_info["text"]
		cdef bint match_case = highlight_info["match_case"]
		cdef bint whole_words = highlight_info["whole_words"]
		cdef bint is_regex = highlight_info["is_regex"]

		if(search_text == None): return
		
		cdef int gutter_width = self.width - text_area_width
		lower_stext = search_text.lower()
		cdef int n = len(search_text)
		cdef int start_line_index, end_line_index
		start_line_index, end_line_index = self.real_line_start_index_visible, self.real_line_end_index_visible
		cdef int y, i, pos, visible_line_index

		for y in range(start_line_index, end_line_index):
			vtext = lines[y]
			lower_vtext = vtext.lower()			

			corpus = (vtext if match_case else lower_vtext)
			if(is_regex or match_case):
				search = search_text
			else:
				search = lower_stext

			pos = -1
			real_pos = CursorPosition(y, pos)
			visible_line_index = self.get_pre_translation_parameters(lines, real_pos, text_area_width, tab_size, word_wrap, hard_wrap)
			
			while(True):
				if(is_regex):
					pos = find_regex(corpus[pos+1:], search)
				elif(whole_words):
					pos = find_whole_word(corpus[pos+1:], search)
				else:
					pos = corpus.find(search, pos+1)
				
				if(pos < 0): break

				for i in range(n):
					real_pos.x = pos + i
					rendered_pos, _ = self.translate_real_curpos_to_rendered_curpos(lines, real_pos, text_area_width, tab_size, word_wrap, hard_wrap, visible_line_index)
					visual_pos = self.translate_rendered_to_visual_pos(rendered_pos, gutter_width)
					self.set_style_single(visual_pos, gc("highlight") | (0 if(self.supports_colors==1) else curses.A_REVERSE))

	# returns a dict() with key=rendered_curpos(sub_line_offset_y, col) and value = real_curpos.x
	cdef get_correspondence(self, line, int width, int tab_size, bint word_wrap, bint hard_wrap):
		col_spans = self.reflow(width, line, tab_size, word_wrap, hard_wrap)
		cdef int n = len(col_spans)
		cdef int x, i, rendered_line_col, sub_line_offset

		correspondence = dict()
		if(n == 0): 
			correspondence[(0,0)] = 0
			return correspondence

		for x in range(len(line)+1):
			rendered_x = self.translate_real_curpos_col_to_rendered_curpos_col(line, tab_size, x)
			rendered_line_col = rendered_x - col_spans[n-1][0] + 1
			sub_line_offset = 0
			for i, cs in enumerate(col_spans):
				if(rendered_x >= cs[0] and rendered_x <= cs[1]):
					rendered_line_col = rendered_x - cs[0]
					sub_line_offset = i
					break
			correspondence[(sub_line_offset, rendered_line_col)] = x
		return correspondence

	cdef translate_rendered_curpos_to_real_curpos(self, lines, int width, rendered_curpos, int tab_size, bint word_wrap, bint hard_wrap):
		cdef int nlines = len(lines)
		cdef int visible_line_counter = -1
		cdef int i, j, sub_line_offset, real_line_index
		cdef int max_col

		try:
			real_line_index, sub_line_offset = self.mapping_rendered_line_to_real_line[rendered_curpos.y]
			correspondence = self.get_correspondence(lines[real_line_index], width, tab_size, word_wrap, hard_wrap)

			real_col = correspondence.get((sub_line_offset, rendered_curpos.x))
			max_col = self.get_max_col_in_correspondence(correspondence, sub_line_offset)

			if(real_col == None): real_col = max_col
			return CursorPosition(real_line_index, real_col)
		except:
			return None

	# returns the maximum real column position possible in the given sub-line as mapped by correspondence
	cdef get_max_col_in_correspondence(self, correspondence, int sub_line_offset):
		cdef int max_col = -1
		for key, value in correspondence.items():
			if(key[0] == sub_line_offset and key[1] >= max_col): max_col = key[1]
		return correspondence.get( (sub_line_offset,max_col) )

	
	cdef get_subline_offset(self, lines, int width, int tab_size, bint word_wrap, bint hard_wrap, real_curpos):
		if(self.all_col_spans == None):
			col_spans = self.reflow(width, lines[real_curpos.y], tab_size, word_wrap, hard_wrap)
		else:
			col_spans = self.all_col_spans[real_curpos.y]

		if(len(col_spans)==0): return (0, col_spans)

		cdef int y
		for y, cs in enumerate(col_spans):
			if(real_curpos.x >= cs[0] and real_curpos.x <= cs[1]): return (y,col_spans)
		
		return (len(col_spans)-1, col_spans)

	cdef translate_real_curpos_col_to_rendered_curpos_col(self, line, int tab_size, int real_col):
		cdef int x = 0, i

		for i in range(real_col):
			x += (tab_size - (x % tab_size)) if(line[i]=="\t") else 1
			
		return x

	# returns the visible-line-index for a line after reflowing: for optimizing translation from real to rendered-curpos (during selection highlighting)
	cdef get_pre_translation_parameters(self, lines, real_curpos, int text_area_width, int tab_size, bint word_wrap, bint hard_wrap):
		cdef int visible_line_index = -1, y
		for y in range(real_curpos.y):
			if(self.all_col_spans == None):
				col_spans = self.reflow(text_area_width, lines[y], tab_size, word_wrap, hard_wrap)
			else:
				col_spans = self.all_col_spans[y]
			visible_line_index += (len(col_spans) if len(col_spans) > 0 else 1)
		return visible_line_index
		
	cdef translate_real_curpos_to_rendered_curpos(self, lines, real_curpos, int text_area_width, int tab_size, bint word_wrap, bint hard_wrap, int visible_line_index = -1):
		cdef int y, i, n, rendered_x, rendered_line_col, current_line_length

		if(visible_line_index < 0):
			visible_line_index = self.mapping_real_line_to_rendered_line[real_curpos.y] - 1
			
		if(self.all_col_spans == None):
			col_spans = self.reflow(text_area_width, lines[real_curpos.y], tab_size, word_wrap, hard_wrap)
		else:
			col_spans = self.all_col_spans[real_curpos.y]
		rendered_x = self.translate_real_curpos_col_to_rendered_curpos_col(lines[real_curpos.y], tab_size, real_curpos.x)
		
		n = len(col_spans)
		if(n == 0): return (CursorPosition(visible_line_index + 1, 0), 0)

		rendered_line_col = col_spans[n-1][1] - col_spans[n-1][0] + 1							# default is: end of the line
		current_line_length = col_spans[n-1][1] - col_spans[n-1][0] + 1

		for i, cs in enumerate(col_spans):
			visible_line_index += 1
			if(rendered_x >= cs[0] and rendered_x <= cs[1]):									# if found before end of the line then return that
				rendered_line_col = rendered_x - cs[0]
				current_line_length = cs[1] - cs[0] + 1
				break
							
		return (CursorPosition(visible_line_index, rendered_line_col), current_line_length)

	cdef _compute_vertical_visibility(self, rendered_curpos):
		cdef int delta
		if(rendered_curpos.y < self.line_start):
			delta = abs(self.line_start - rendered_curpos.y)
			self.line_start -= delta
			self.line_end -= delta
		elif(rendered_curpos.y >= self.line_end):
			delta = abs(rendered_curpos.y - self.line_end)
			self.line_end += delta + 1
			self.line_start += delta + 1
	
	cdef _compute_horizontal_visibility(self, rendered_curpos, int rendered_line_length):
		cdef int delta
		if(rendered_curpos.x < self.col_start):
			delta = abs(self.col_start - rendered_curpos.x)
			self.col_start -= delta
			self.col_end -= delta
		elif(rendered_curpos.x >= self.col_end):
			delta = abs(rendered_curpos.x - self.col_end)
			self.col_end += delta + 1
			self.col_start += delta + 1
		
		# the following ensures when deleting characters, atleast 1 character back is visible
		if(self.col_start > 0 and self.col_start == rendered_line_length):
			self.col_start -= 1
			self.col_end -= 1

	# computes line-start, line-end, col-start, col-end, and returns rendered-curpos
	cdef scroll(self, lines, real_curpos, int text_area_width, int tab_size, bint word_wrap, bint hard_wrap):
		cdef int rendered_line_length
		rendered_curpos, rendered_line_length = self.translate_real_curpos_to_rendered_curpos(lines, real_curpos, text_area_width, tab_size, word_wrap, hard_wrap)
		self._compute_vertical_visibility(rendered_curpos)
		self._compute_horizontal_visibility(rendered_curpos, rendered_line_length)
		return rendered_curpos

	# <--------- called externally: do not Cythonize() ---------------------->

	def recompute(self, real_curpos, tab_size, word_wrap, hard_wrap, forced=True):
		if(self.buffer == None): return

		gutter_width = self._get_gutter_width(self.line_end)
		self.last_gutter_width = gutter_width
		text_area_width = self.width - gutter_width

		if(forced or self.last_text_area_width != text_area_width or self.last_tab_size != tab_size or self.last_word_wrap != word_wrap or self.last_hard_wrap != hard_wrap):
			self.reflow_all(text_area_width, self.buffer.lines, tab_size, word_wrap, hard_wrap)
			self.last_text_area_width = text_area_width
			self.last_tab_size = tab_size
			self.last_word_wrap = word_wrap
			self.last_hard_wrap = hard_wrap

	# render text data to screen buffer
	def render(self, real_curpos, tab_size, word_wrap, hard_wrap, selection_info, highlight_info, is_in_focus, slave_cursors, stylize = True):
		# There are 3 types of cursor positions:
		# 1. real curpos = w.r.t. real line (passed as parameter to this function)
		# 2. rendered curpos = after taking tab & wrapping into consideration
		# 3. visual curpos = w.r.t. the screen buffer (portion that is actually displayed)

		# initialize
		self.clear()
		y = 0

		# determine line(start,end) and col(start,end): and return rendered_curpos
		# Circular dependency: scroll() requires gutter_width, but gutter_width requires line_end which is computed by scroll()
		# won't be a problem if you allow line numbers to start from screen-edge: that space will be taken up if user scrolls so much that 1/2 digits are added in the next scroll()
		
		#t1 = datetime.datetime.now()
		rendered_curpos = self.scroll(self.buffer.lines, real_curpos, self.width - self._get_gutter_width(self.line_end), tab_size, word_wrap, hard_wrap)

		# set up lines
		lines = self.buffer.lines
		nlines = len(lines)
		
		# self.line_start contains the 1st visible line index: 
		# 0 = 1st real line always; 
		# 1 = either 2nd real line (if wrapping is OFF), or second portion of 1st real line (if wrapping is ON and 1st real line is longer than width-gutter_width)
		
		# compute line_end and gutter_width
		gutter_width = self._get_gutter_width(self.line_end)
		self.last_gutter_width = gutter_width
		text_area_width = self.width - gutter_width

		#t2 = datetime.datetime.now()
		
		if(self.last_text_area_width != text_area_width or self.last_tab_size != tab_size or self.last_word_wrap != word_wrap or self.last_hard_wrap != hard_wrap):
			self.all_col_spans = None
			self.last_text_area_width = text_area_width
			self.last_tab_size = tab_size
			self.last_word_wrap = word_wrap
			self.last_hard_wrap = hard_wrap
		
		self.set_gutter_style(gutter_width)
		if(self.all_col_spans == None):
			self.reflow_all(text_area_width, self.buffer.lines, tab_size, word_wrap, hard_wrap)

		#t3 = datetime.datetime.now()

		# determine the first line to be displayed
		real_line_start, line_start_col_spans, line_start_offset = self._get_line_start(nlines, lines)
		self.real_line_start_index_visible = real_line_start		# store for use in highlighting
		
		# show (if any) remaining wrapped text from previous line
		if(line_start_offset > 0):
			# expand the tabs to get the whole line
			text = lines[real_line_start].expandtabs(tab_size)

			# for each remaining wrapped-line, do:
			for y in range( len(line_start_col_spans) - line_start_offset ):
				if(y >= self.height): break												# when whole screen is filled with a single-wrapped line
				cs = line_start_col_spans[line_start_offset + y]						# get the colspan
				cs_start = cs[0]							# inclusive
				cs_end = cs[1] + 1							# exclusive
				vtext = text[cs_start : cs_end]
				if(self.col_start < cs_end - cs_start):
					vtext = vtext[self.col_start:]
					self.putstr(y, gutter_width, vtext)
			
			# increment line-start so that it starts on a fresh real-line
			real_line_start += 1			
			y += 1

		# print lines:
		# y holds the screenbuffer offset: 0 = 1st visible line (line portion in case of wrapping)
		# line_index holds the real buffer line index: 0 = 1st line in the document
		line_index = real_line_start
		current_line_number_y = -1
		while(y < self.height and line_index < nlines):
			if(self.show_line_numbers):
				self.put_line_number(y, line_index+1, gutter_width)
				if(line_index == real_curpos.y): current_line_number_y = y

			text = lines[line_index].expandtabs(tab_size)
			col_spans = self.all_col_spans[line_index]
			
			for i in range( len(col_spans) ):
				if(y >= self.height): break				
				cs = col_spans[i]							# get the colspan
				cs_start = cs[0]							# inclusive
				cs_end = cs[1] + 1							# exclusive
				vtext = text[cs_start : cs_end]				
				if(self.col_start < cs_end - cs_start):
					vtext = vtext[self.col_start:]
					self.putstr(y, gutter_width, vtext)
				y+=1
				
			# increment line-start so that it starts on a fresh real-line
			line_index += 1
			if(len(col_spans) == 0): y += 1

		self.real_line_end_index_visible = line_index			# store for use in highlighting
		
		#t4 = datetime.datetime.now()

		# show scrollbars
		if(self.show_scrollbars):
			self.putstr(0, 0, "\u25b4")
			self.putstr(self.height-1, 0, "\u25be")
			self.set_style(0, 0, 1, gc("scrollbar-buttons"))
			self.set_style(self.height-1, 0, 1, gc("scrollbar-buttons"))

			if(self.height >= self.total_rendered_lines):
				bar_height = self.height - 2
				bar_offset = 0
			else:
				bar_height = round((self.height / self.total_rendered_lines) * (self.height-2))
				bar_offset = round(( self.line_start / self.total_rendered_lines) * (self.height-2))

			bar_height = max([min([bar_height, self.height-2]), 1])
			bar_offset = max([min([bar_offset, self.height-1]), 0])

			for i in range(1, self.height-1):
				if(i-1 >= bar_offset and i-1 < bar_offset+bar_height):
					self.putstr(i,0,"\u2588")
					self.set_style(i, 0, 1, gc("scrollbar-bar"))
				else:
					self.putstr(i,0,"\u2503")
					self.set_style(i, 0, 1, gc("scrollbar-empty"))

		# stylize text
		if(stylize): self.perform_syntax_highlighting(lines, text_area_width, real_curpos, tab_size, word_wrap, hard_wrap)
		
		# highlight text
		if(highlight_info != None): self.perform_search_highlighting(lines, text_area_width, real_curpos, tab_size, word_wrap, hard_wrap, highlight_info)
		if(selection_info != None): self.perform_selection_highlighting(lines, text_area_width, real_curpos, rendered_curpos, tab_size, word_wrap, hard_wrap, selection_info)
			
		# compute cursor position and place it
		if(is_in_focus):
			# add primary cursor
			visual_curpos = self.translate_rendered_to_visual_pos(rendered_curpos, gutter_width)
			self.put_cursor(visual_curpos.y, visual_curpos.x)

			# add slave cursors
			if(slave_cursors != None):
				for sc in slave_cursors:
					rendered_slave_curpos, _ = self.translate_real_curpos_to_rendered_curpos(self.buffer.lines, sc, text_area_width, tab_size, word_wrap, hard_wrap)
					visual_slave_curpos = self.translate_rendered_to_visual_pos(rendered_slave_curpos, gutter_width)
					self.put_cursor(visual_slave_curpos.y, visual_slave_curpos.x)

			# highlight current line
			if(self.show_line_numbers): self.highlight_line(current_line_number_y, gutter_width)

		#t5 = datetime.datetime.now()

		#time_scroll = t2 - t1
		#time_reflow = t3 - t2
		#time_lines = t4 - t3
		#time_formatting = t5 - t4

		#log(f"{time_scroll} | {time_reflow} | {time_lines} | {time_formatting}")

		return rendered_curpos, text_area_width
	
	def translate_real_to_visual_curpos(self, real_curpos, lines, width, tab_size, word_wrap, hard_wrap):
		text_area_width = width - self.last_gutter_width
		rendered_curpos, _ = self.translate_real_curpos_to_rendered_curpos(lines, real_curpos, text_area_width, tab_size, word_wrap, hard_wrap)
		visual_curpos = self.translate_rendered_to_visual_pos(rendered_curpos, self.last_gutter_width)
		return visual_curpos

	def get_selection_endpoints(self, sel_start, sel_end):
		if(not self.is_start_before_end(sel_start, sel_end)): 
			sel_start, sel_end = sel_end, sel_start
		return(sel_start, sel_end)

	# draw the screen-buffer on screen
	def draw(self, offset_y, offset_x):
		# optimized drawing routine: call addstr() only if style changes
		cdef int x, y, last_style_x
		for y in range(self.height):
			last_style = self.style_buffer[y][0]
			last_style_x = 0
			for x in range(1, self.width):
				if(self.style_buffer[y][x] == last_style): continue
				self.win.addstr(offset_y + y, offset_x + last_style_x, self.screen_buffer[y][last_style_x:x], last_style)
				last_style = self.style_buffer[y][x]
				last_style_x = x
			self.win.addstr(offset_y + y, offset_x + last_style_x, self.screen_buffer[y][last_style_x:self.width], last_style)

	# <------------------------------- mouse handling functions ----------------------------------->
	def get_curpos_after_click(self, y, x, lines, width, tab_size, word_wrap, hard_wrap):
		visual_curpos = CursorPosition(y, x)
		rendered_curpos = self.translate_visual_to_rendered_pos(visual_curpos, self.last_gutter_width)
		if(rendered_curpos == None): return None
		real_curpos = self.translate_rendered_curpos_to_real_curpos(lines, width, rendered_curpos, tab_size, word_wrap, hard_wrap)
		return real_curpos
	
	# <------------------------------- key handler functions ----------------------------------->
	def get_curpos_after_move_left(self, real_curpos, tab_size, word_wrap, hard_wrap):
		lines = self.buffer.lines
		if(real_curpos.x == 0 and real_curpos.y == 0):
			return copy.copy(real_curpos)
		elif(real_curpos.x > 0):
			return CursorPosition(real_curpos.y, real_curpos.x - 1)
		elif(real_curpos.x == 0):
			prev_line_width = len(lines[real_curpos.y - 1])
			return CursorPosition(real_curpos.y - 1, prev_line_width)
	
	def get_curpos_after_move_right(self, real_curpos, tab_size, word_wrap, hard_wrap):
		lines = self.buffer.lines
		nlines = len(lines)
		clw = len(lines[real_curpos.y])
		if(real_curpos.y == nlines-1 and real_curpos.x == clw):
			return copy.copy(real_curpos)
		elif(real_curpos.x < clw):
			return CursorPosition(real_curpos.y, real_curpos.x + 1)
		elif(real_curpos.x == clw):
			return CursorPosition(real_curpos.y + 1, 0)

	def get_curpos_after_move_up(self, real_curpos, tab_size, word_wrap, hard_wrap):
		_, width = self.render(real_curpos, tab_size, word_wrap, hard_wrap, None, None, True, None, False)
		lines = self.buffer.lines
		y, col_spans = self.get_subline_offset(lines, width, tab_size, word_wrap, hard_wrap, real_curpos)
		if(y == 0 and real_curpos.y == 0):
			return copy.copy(real_curpos)
		else:
			rendered_curpos, _ = self.translate_real_curpos_to_rendered_curpos(lines, real_curpos, width, tab_size, word_wrap, hard_wrap)
			rendered_curpos.y -= 1
			return self.translate_rendered_curpos_to_real_curpos(lines, width, rendered_curpos, tab_size, word_wrap, hard_wrap)
		
	def get_curpos_after_move_down(self, real_curpos, tab_size, word_wrap, hard_wrap):
		rendered_curpos, width = self.render(real_curpos, tab_size, word_wrap, hard_wrap, None, None, True, None, False)
		lines = self.buffer.lines
		y, col_spans = self.get_subline_offset(lines, width, tab_size, word_wrap, hard_wrap, real_curpos)
		
		if((y == len(col_spans)-1 or (y==0 and len(col_spans)==0)) and real_curpos.y == len(lines)-1):
			return copy.copy(real_curpos)
		else:
			rendered_curpos.y += 1
			new_real_curpos = self.translate_rendered_curpos_to_real_curpos(lines, width, rendered_curpos, tab_size, word_wrap, hard_wrap)
			return new_real_curpos

	def get_curpos_after_move_home(self, real_curpos, tab_size, word_wrap, hard_wrap):
		lines = self.buffer.lines
		i = self.get_first_nonwhitespace_position(lines, real_curpos.y)
		if(real_curpos.x == i):
			return CursorPosition(real_curpos.y, 0)
		else:
			return CursorPosition(real_curpos.y, i)

	def get_curpos_after_move_end(self, real_curpos, tab_size, word_wrap, hard_wrap):
		lines = self.buffer.lines
		w = len(lines[real_curpos.y])
		return CursorPosition(real_curpos.y, w)

	cdef get_first_nonwhitespace_position(self, lines, int y):
		line = lines[y]
		cdef int w = len(line)
		cdef int i = 0
		for i in range(w):
			if(line[i] != '\t' and line[i] != ' '): break
		return i