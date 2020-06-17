from ash.widgets import *
from ash.widgets.utils.utils import *
from ash.widgets.utils.formatting import *

import copy

class CursorPosition:
	def __init__(self, y, x):
		self.y = y
		self.x = x

	def __str__(self):
		return "Ln " + str(self.y+1) + ", Col " + str(self.x+1)

class Editor(Widget):
	def __init__(self, parent, y, x, height, width):
		super().__init__(WIDGET_TYPE_EDITOR, True, True)
		self.y = y
		self.x = x
		self.height = height
		self.full_width = width
		self.line_number_width = 6
		self.width = width - self.line_number_width - 1
		self.parent = parent
		self.is_in_focus = False

		self.lines = [ "" ]
		self.curpos = CursorPosition(0,0)

		self.separators = "~`!@#$%^&*()-_=+\\|[{]};:\'\",<.>/? "
		self.charset = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789"
		self.charset += self.separators
		
		self.word_wrap = False
		self.selection_mode = False
		self.sel_start = None
		self.sel_end = None
		self.tab_size = 4
		
		self.line_start = 0
		self.line_end = self.height
		self.col_start = 0
		self.col_end = self.width

		self.set_general_theme(gc(), gc(COLOR_BLACK_ON_YELLOW), gc(COLOR_GRAY_ON_BLACK), gc(COLOR_YELLOW_ON_BLACK))
		self.set_language_theme(None, None, None, None)
		self.set_comment_symbol(None, None, None)
		self.focus()
	
	def focus(self):
		self.is_in_focus = True
		self.repaint()

	def blur(self):
		self.is_in_focus = False
		self.repaint()

	def get_cursor_position(self):
		return str(self.curpos)

	def set_word_wrap(self, wrap):
		self.word_wrap = wrap
		self.repaint()

	def set_general_theme(self, text_theme, selection_theme, line_number_theme, highlighted_line_number_theme):
		self.text_theme = text_theme
		self.selection_theme = selection_theme
		self.line_number_theme = line_number_theme
		self.highlighted_line_number_theme = highlighted_line_number_theme

	def set_language_theme(self, keyword_theme1, keyword_theme2, string_theme, comment_theme):
		self.keyword_theme1 = keyword_theme1
		self.keyword_theme2 = keyword_theme2
		self.string_theme = string_theme
		self.comment_theme = comment_theme

	def set_comment_symbol(self, single_line_comment, multiline_comment_start, multiline_comment_end):
		self.single_line_comment = single_line_comment
		self.multiline_comment_start = multiline_comment_start
		self.multiline_comment_end = multiline_comment_end

	def perform_action(self, ch):
		self.focus()

		if(ch == -1):
			self.repaint()
			return None
		
		if(ch == curses.KEY_BACKSPACE):
			self.__handle_backspace_key(ch)
		elif(ch == curses.KEY_DC):
			self.__handle_delete_key(ch)
		elif(ch in [ curses.KEY_HOME, curses.KEY_END ]):
			self.__handle_home_end_keys(ch)
		elif(ch in [ curses.KEY_LEFT, curses.KEY_RIGHT, curses.KEY_UP, curses.KEY_DOWN ]):
			self.__handle_arrow_keys(ch)
		elif(ch in [ curses.KEY_PPAGE, curses.KEY_NPAGE ]):
			self.__handle_page_navigation_keys(ch)
		elif(ch in [ curses.KEY_SLEFT, curses.KEY_SRIGHT, curses.KEY_SR, curses.KEY_SF ]):
			self.__handle_shift_arrow_keys(ch)
		elif(is_ctrl_arrow(ch, "LEFT") or is_ctrl_arrow(ch, "RIGHT")):
			self.__handle_ctrl_arrow_keys(ch)
		elif(is_tab(ch) or ch == curses.KEY_BTAB):
			self.__handle_tab_keys(ch)
		elif(is_newline(ch)):
			self.__handle_newline(ch)
		elif(str(chr(ch)) in self.charset):
			self.__handle_printable_character(ch)
		else:
			curses.beep()
		
		self.repaint()

	def __determine_vertical_visibility(self):
		if(self.curpos.y < self.line_start):
			delta = abs(self.line_start - self.curpos.y)
			self.line_start -= delta
			self.line_end -= delta
		elif(self.curpos.y >= self.line_end):
			delta = abs(self.curpos.y - self.line_end)
			self.line_end += delta + 1
			self.line_start += delta + 1
		return(self.curpos.y - self.line_start)

	def __determine_horizontal_visibility(self):
		ctab = (self.tab_size - 1) * self.lines[self.curpos.y][0:self.curpos.x].count("\t")
		curpos_col = self.curpos.x + ctab		# actual cursor position w.r.t whitespaces

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
		
	def __is_in_selection(self, line_index):
		if(self.selection_mode):
			if(is_start_before_end(self.sel_start, self.sel_end)):
				return(True if (line_index >= self.sel_start.y and line_index <= self.sel_end.y) else False)
			else:
				return(True if (line_index >= self.sel_end.y and line_index <= self.sel_start.y) else False)
		else:
			return False

	def __get_selection_endpoints(self):
		forward_sel = is_start_before_end(self.sel_start, self.sel_end)
		if(forward_sel):
			start = copy.copy(self.sel_start)
			end = copy.copy(self.sel_end)
		else:
			start = copy.copy(self.sel_end)
			end = copy.copy(self.sel_start)
		return (start, end)

	def __delete_selected_text(self):
		start, end = self.__get_selection_endpoints()
		
		# .........XXXXXXXXXXXX 0 start		lc=2
		# XXXXXXXXXXXXXXXXXXXXX 1
		# XXXXXXXXXXXXXXXXXXXXX 2
		# XXXXXXXXXXX*......... 3 end

		# .........XXXXXXXXXXXX 0 start		lc=1
		# XXXXXXXXXXXXXXXXXXXXX 1
		# XXXXXXXXXXX*......... 2 end

		# .........XXXXXXXXXXXX 0 start		lc=0
		# XXXXXXXXXXX*......... 1 end

		if(start.y == end.y):
			# .....XXXXXXX*........	0 start, end
			sel_len = end.x - start.x
			self.lines[start.y] = self.lines[start.y][0:start.x] + self.lines[start.y][end.x:]
		else:
			lc = end.y - start.y - 1
			while(lc > 0):
				self.lines.pop(start.y + 1)
				self.curpos.y -= 1
				end.y -= 1
				lc -= 1

			# .........				0 start
			# XXXXXXXXXXX*.........	1 end

			self.lines[start.y] = self.lines[start.y][0:start.x]

			# .........				0 start
			# *.........			1 end

			self.lines[end.y] = self.lines[end.y][end.x:]

			# .........*........... 0 start, end

			text = self.lines[end.y]
			self.lines.pop(end.y)
			self.curpos.y = start.y
			self.curpos.x = len(self.lines[start.y])
			self.lines[start.y] += text
		
		self.selection_mode = False
	
	def __shift_selection_right(self):
		start, end = self.__get_selection_endpoints()
		for i in range(start.y, end.y+1):
			self.lines[i] = "\t" + self.lines[i]
		self.curpos.x += 1
		self.sel_start.x += 1
		self.sel_end.x += 1

	def __shift_selection_left(self):
		start, end = self.__get_selection_endpoints()

		has_tab_in_all = True
		for i in range(start.y, end.y+1):
			if(not self.lines[i].startswith("\t")):
				has_tab_in_all = False
				break

		if(has_tab_in_all):
			for i in range(start.y, end.y+1):
				self.lines[i] = self.lines[i][1:]
			self.curpos.x -= 1
			self.sel_start.x -= 1
			self.sel_end.x -= 1


	def __print_selection(self, line_index):
		start, end = self.__get_selection_endpoints()
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


	def repaint(self):
		curses.curs_set(self.is_in_focus)

		curpos_row = self.__determine_vertical_visibility()
		curpos_col = self.__determine_horizontal_visibility()
		nlines = len(self.lines)

		for i in range(self.line_start, self.line_end):
			if(i >= nlines): break

			# print line number
			self.parent.addstr(self.y + i - self.line_start, self.x, pad_left_str(str(i+1), self.line_number_width), self.highlighted_line_number_theme if self.curpos.y == i else self.line_number_theme)
			
			# print the text
			text = self.lines[i].replace("\t", " " * self.tab_size)
			if(self.col_start < len(text)):
				vtext = text[self.col_start:] if self.col_end > len(text) else text[self.col_start:self.col_end]
				
				if(self.__is_in_selection(i)):
					self.__print_selection(i)
				else:
					self.parent.addstr(self.y + i - self.line_start, self.x + self.line_number_width + 1, vtext, self.text_theme)
		
		# position the cursor
		self.parent.move(self.y + curpos_row, self.x + self.line_number_width + 1 + curpos_col)
		
	def __str__(self):
		pass

	def __handle_arrow_keys(self, ch):
		row = self.curpos.y
		col = self.curpos.x
		clen = len(self.lines[row])
		nlen = len(self.lines)
		self.selection_mode = False		# turn off selection mode
		if(ch == curses.KEY_LEFT):
			if(row == 0 and col == 0):
				curses.beep()
			elif(col == 0):
				self.curpos.y -= 1
				self.curpos.x = len(self.lines[row-1])
			else:
				self.curpos.x -= 1
		elif(ch == curses.KEY_RIGHT):
			if(row == nlen-1 and col == clen):
				curses.beep()
			elif(col == clen):
				self.curpos.y += 1
				self.curpos.x = 0
			else:
				self.curpos.x += 1
		elif(ch == curses.KEY_DOWN):
			if(row == nlen-1):
				curses.beep()
			else:
				if(self.curpos.x > len(self.lines[row+1])):
					# cannot preserve column
					self.curpos.x = len(self.lines[row+1])
				self.curpos.y += 1
		elif(ch == curses.KEY_UP):
			if(row == 0):
				curses.beep()
			else:
				if(self.curpos.x > len(self.lines[row-1])):
					# cannot preserve column
					self.curpos.x = len(self.lines[row-1])
				self.curpos.y -= 1

		self.curpos.x = min([self.curpos.x, len(self.lines[self.curpos.y])])
		self.curpos.x = max(0, self.curpos.x)
		self.curpos.y = min([self.curpos.y, len(self.lines)-1])
		self.curpos.y = max(0, self.curpos.y)
		
	def __get_leading_whitespaces(self, line_index):
		text = self.lines[line_index]
		nlen = len(text)
		ws = ""
		for i in range(nlen):
			if(text[i] == " " or text[i] == "\t"): 
				ws += text[i]
			else:
				break
		return ws

	def __handle_ctrl_arrow_keys(self, ch):
		if(is_ctrl_arrow(ch, "LEFT")):
			if(self.curpos.x == 0):
				curses.beep()
			else:
				for i in range(self.curpos.x-1, -1, -1):
					c = self.lines[self.curpos.y][i]
					if(c in self.separators):
						self.curpos.x = i
						return
				self.curpos.x = 0
		elif(is_ctrl_arrow(ch, "RIGHT")):
			nlen = len(self.lines[self.curpos.y])
			if(self.curpos.x == nlen):
				curses.beep()
			else:
				for i in range(self.curpos.x+1, nlen):
					c = self.lines[self.curpos.y][i]
					if(c in self.separators):
						self.curpos.x = i
						return
				self.curpos.x = nlen

	def __handle_shift_arrow_keys(self, ch):
		row = self.curpos.y
		col = self.curpos.x
		nlen = len(self.lines)
		clen = len(self.lines[row])

		if(not self.selection_mode):
			self.selection_mode = True
			self.sel_start = copy.copy(self.curpos)
		
		if(ch == curses.KEY_SLEFT):
			if(row == 0 and col == 0):
				curses.beep()
			elif(col == 0):
				self.curpos.y -= 1
				self.curpos.x = len(self.lines[row-1])
			else:
				self.curpos.x -= 1
		elif(ch == curses.KEY_SRIGHT):
			if(row == nlen-1 and col == clen):
				curses.beep()
			elif(col == clen):
				self.curpos.y += 1
				self.curpos.x = 0
			else:
				self.curpos.x += 1
		elif(ch == curses.KEY_SF):
			if(row == nlen-1):
				curses.beep()
			else:
				if(self.curpos.x > len(self.lines[row+1])):
					# cannot preserve column
					self.curpos.x = len(self.lines[row+1])
				self.curpos.y += 1
		elif(ch == curses.KEY_SR):
			if(row == 0):
				curses.beep()
			else:
				if(self.curpos.x > len(self.lines[row-1])):
					# cannot preserve column
					self.curpos.x = len(self.lines[row-1])
				self.curpos.y -= 1

		self.curpos.x = min([self.curpos.x, len(self.lines[self.curpos.y])])
		self.curpos.x = max(0, self.curpos.x)
		self.curpos.y = min([self.curpos.y, len(self.lines)-1])
		self.curpos.y = max(0, self.curpos.y)
		self.sel_end = copy.copy(self.curpos)

	def __handle_delete_key(self, ch):
		if(self.selection_mode):
			self.__delete_selected_text()
			return
		
		text = self.lines[self.curpos.y]
		clen = len(text)
		col = self.curpos.x

		if(self.curpos.y == len(self.lines)-1 and col == clen):
			curses.beep()
			return
		
		if(col == clen):
			ntext = self.lines[self.curpos.y + 1]
			self.lines.pop(self.curpos.y + 1)
			self.lines[self.curpos.y] += ntext
		else:
			left = text[0:col] if col > 0 else ""
			right = text[col+1:] if col < len(text)-1 else ""
			self.lines[self.curpos.y] = left + right
			
	def __handle_backspace_key(self, ch):
		if(self.selection_mode):
			self.__delete_selected_text()
			return		

		text = self.lines[self.curpos.y]
		col = self.curpos.x

		if(col == 0 and self.curpos.y == 0):
			curses.beep()
			return

		if(col == 0):
			self.lines.pop(self.curpos.y)
			temp = len(self.lines[self.curpos.y-1])
			self.lines[self.curpos.y - 1] += text
			self.curpos.x = temp
			self.curpos.y -= 1
		else:
			left = text[0:col-1] if col > 1 else ""
			right = text[col:] if col < len(text) else ""
			self.lines[self.curpos.y] = left + right
			self.curpos.x -= 1		

	def __handle_home_end_keys(self, ch):
		if(ch == curses.KEY_HOME):
			# toggle between beginning of line and beginning of indented-code
			if(self.curpos.x == 0):
				self.curpos.x = len(self.__get_leading_whitespaces(self.curpos.y))
			else:
				self.curpos.x = 0
		elif(ch == curses.KEY_END):
			self.curpos.x = len(self.lines[self.curpos.y])

	def __handle_tab_keys(self, ch):
		if(self.selection_mode):
			if(is_tab(ch)):
				self.__shift_selection_right()
				return
			elif(ch == curses.KEY_BTAB):
				self.__shift_selection_left()
				return

		col = self.curpos.x
		text = self.lines[self.curpos.y]

		if(is_tab(ch)):
			left = text[0:col] if col > 0 else ""
			right = text[col:] if len(text) > 0 else ""
			self.lines[self.curpos.y] = left + "\t" + right
			self.curpos.x += 1
		elif(ch == curses.KEY_BTAB):
			if(col == 0):
				curses.beep()
			elif(col == len(self.__get_leading_whitespaces(self.curpos.y))):
				left = text[0:col-1] if col > 1 else ""
				right = text[col:] if col < len(text) else ""
				self.lines[self.curpos.y] = left + right
				self.curpos.x -= 1
			else:
				curses.beep()

	def __handle_newline(self, ch):
		if(self.selection_mode): self.__delete_selected_text()

		text = self.lines[self.curpos.y]
		col = self.curpos.x
		left = text[0:col] if col > 0 else ""
		right = text[col:] if len(text) > 0 else ""
		whitespaces = self.__get_leading_whitespaces(self.curpos.y)
		right = whitespaces + right
		self.lines[self.curpos.y] = left
		if(len(self.lines) == self.curpos.y + 1):
			self.lines.append(right)
		else:
			self.lines.insert(self.curpos.y + 1, right)
		self.curpos.y += 1
		self.curpos.x = len(whitespaces)
	
	def __handle_printable_character(self, ch):
		if(self.selection_mode): self.__delete_selected_text()
		
		sch = str(chr(ch))
		text = self.lines[self.curpos.y]
		col = self.curpos.x
		left = text[0:col] if col > 0 else ""
		right = text[col:] if len(text) > 0 else ""
		self.lines[self.curpos.y] = left + sch + right
		self.curpos.x += 1
	
	def __handle_page_navigation_keys(self, ch):
		h = self.height
		nlen = len(self.lines)
		if(ch == curses.KEY_PPAGE):			# pg-up
			if(self.curpos.y == 0):
				if(self.curpos.x == 0):
					curses.beep()
				else:
					self.curpos.x = 0
					return
			elif(self.curpos.y <= h):
				self.curpos.y = 0
			else:
				self.curpos.y -= h-1
			self.curpos.x = 0
		elif(ch == curses.KEY_NPAGE):		# pg-down
			if(self.curpos.y == nlen-1):
				if(self.curpos.x == len(self.lines[nlen-1])):
					curses.beep()
				else:
					self.curpos.x = len(self.lines[nlen-1])
					return
			elif(nlen - self.curpos.y <= h):
				self.curpos.y = nlen-1
			else:
				self.curpos.y += h-1
			self.curpos.x = 0

	def find(self, str):
		pass

	def find_and_replace(self, strf, strr):
		pass