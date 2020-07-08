# ---------------------------------------------------------------------------------------------
#  Copyright (c) Akash Nag. All rights reserved.
#  Licensed under the MIT License. See LICENSE.md in the project root for license information.
# ---------------------------------------------------------------------------------------------

# This module is a helper class for Editor

from ash.gui import *
from ash.formatting.formatting import *
from ash.core.utils import *
from ash.core.dataUtils import *

class EditorUtility:
	def __init__(self, ed):
		self.ed = ed

	# delete the selected text
	def delete_selected_text(self):
		start, end = self.ed.get_selection_endpoints()
		del_text = ""

		if(start.y == end.y):
			sel_len = end.x - start.x
			del_text = self.ed.buffer.lines[start.y][start.x:end.x]
			self.ed.buffer.lines[start.y] = self.ed.buffer.lines[start.y][0:start.x] + self.ed.buffer.lines[start.y][end.x:]			
		else:
			del_text = self.ed.buffer.lines[start.y][start.x:] + self.ed.buffer.newline
						
			# delete entire lines between selection start and end
			lc = end.y - start.y - 1
			while(lc > 0):
				del_text += self.ed.buffer.lines[start.y+1] + self.ed.buffer.newline
				self.ed.buffer.lines.pop(start.y + 1)
				self.ed.curpos.y -= 1
				end.y -= 1
				lc -= 1

			# delete a portion of the selection start line
			self.ed.buffer.lines[start.y] = self.ed.buffer.lines[start.y][0:start.x]

			# delete a portion of the selection end line
			del_text += self.ed.buffer.lines[end.y][0:end.x]
			self.ed.buffer.lines[end.y] = self.ed.buffer.lines[end.y][end.x:]

			# bring the selection end line up towards the end of the selection start line
			text = self.ed.buffer.lines[end.y]
			self.ed.buffer.lines.pop(end.y)
			self.ed.curpos.y = start.y
			self.ed.curpos.x = len(self.ed.buffer.lines[start.y])
			self.ed.buffer.lines[start.y] += text
		
		# turn off selection mode
		self.ed.selection_mode = False
		self.ed.curpos.x = max(self.ed.curpos.x, 0)
		self.ed.curpos.x = min(self.ed.curpos.x, len(self.ed.buffer.lines[self.ed.curpos.y]))
		
		return del_text

	# returns the selected text
	def get_selected_text(self):
		start, end = self.ed.get_selection_endpoints()
		sel_text = ""

		if(start.y == end.y):
			sel_len = end.x - start.x
			sel_text = self.ed.buffer.lines[start.y][start.x:end.x]
		else:
			sel_text = self.ed.buffer.lines[start.y][start.x:] + self.ed.buffer.newline
			for row in range(start.y+1, end.y):
				sel_text = self.ed.buffer.lines[row] + self.ed.buffer.newline
			sel_text += self.ed.buffer.lines[end.y][0:end.x]

		return sel_text

	# increase indent of selected lines
	def shift_selection_right(self):
		start, end = self.ed.get_selection_endpoints()
		for i in range(start.y, end.y+1):
			self.ed.buffer.lines[i] = "\t" + self.ed.buffer.lines[i]
		self.ed.curpos.x += 1
		self.ed.sel_start.x += 1
		self.ed.sel_end.x += 1
		
		return True

	# decrease indent of selected lines
	def shift_selection_left(self):
		start, end = self.ed.get_selection_endpoints()

		# check if all lines have at least 1 indent
		has_tab_in_all = True
		for i in range(start.y, end.y+1):
			if(not self.ed.buffer.lines[i].startswith("\t")):
				has_tab_in_all = False
				break

		# decrease indent only if all lines are indented
		if(has_tab_in_all):
			for i in range(start.y, end.y+1):
				self.ed.buffer.lines[i] = self.ed.buffer.lines[i][1:]
			self.ed.curpos.x -= 1
			self.ed.sel_start.x -= 1
			self.ed.sel_end.x -= 1
			
			return True
		else:
			return False

	def get_leading_whitespaces_from_text(self, text):
		nlen = len(text)
		ws = ""
		for i in range(nlen):
			if(text[i] == " " or text[i] == "\t"): 
				ws += text[i]
			else:
				break
		return ws

	# returns the block of leading whitespaces on a given line 
	def get_leading_whitespaces(self, line_index):
		return self.get_leading_whitespaces_from_text(self.ed.buffer.lines[line_index])
		
	# returns the block of leading whitespaces on a given rendered line 
	def get_leading_whitespaces_rendered(self, line_index):
		return self.get_leading_whitespaces_from_text(self.ed.rendered_lines[line_index])
		
	# returns the selection endpoints in the correct order
	def get_selection_endpoints(self):
		forward_sel = is_start_before_end(self.ed.sel_start, self.ed.sel_end)
		if(forward_sel):
			start = copy.copy(self.ed.sel_start)
			end = copy.copy(self.ed.sel_end)
		else:
			start = copy.copy(self.ed.sel_end)
			end = copy.copy(self.ed.sel_start)
		return (start, end)

	# performs word-wrapping on a given line, and returns the sub-lines formed thus
	def soft_wrap(self, text, width, break_words):
		# assumes 'text' does not contain newlines
		if("\n" in text): raise(Exception("Newline found during wrap operation!"))

		separators = "~!@#$%^&*()-=+\\|[{]};:,<.>/? \t\n"
		text += "\n"		# append newline to make life easier
		n = len(text) - 1
		lines = list()
		while(n > width):
			sub = text[0:width]
			if(sub[-1] in separators or text[width] == "\n"):
				# we are lucky to have the line end in a separator
				lines.append(sub)
				text = text[width:]
				n -= width
				if(text == "\n"): text = ""
			else:
				ls = len(sub)
				rsub = str_reverse(sub)
				index = next((i for i, ch in enumerate(rsub) if ch in separators), None)
				if(index == None):
					# no separator found before intended line-break
					if(break_words):
						# breaking words are allowed: switch to hard-wrap
						lines.append(sub)
						text = text[width:]
						n -= width
						if(text == "\n"): text = ""
					else:
						# breaking words are not allowed: find next separator position
						index = next((i for i, ch in enumerate(text) if ch in separators), None)
						# index will never be None bcoz we have appended newline to end
						if(text[index] == "\n"):
							lines.append(text[0:index])
							text = ""
							n = 0
						else:
							sub = text[0:index+1]
							text = text[index+1:]
							lines.append(sub)
							n -= index+1
				else:
					sub = text[0:ls-index]
					lines.append(sub)
					text = text[ls-index:]
					n -= (ls-index)
		
		lines.append(text[0:n])
		return lines

	# returns the list of sub-lines formed from wrapping a given line
	# high-level function: calles soft_wrap() internally
	def wrapped(self, line, width, word_wrap, break_words):
		sub_lines = list()
		if(not word_wrap):
			sub_lines.append(line)
		else:
			sub_lines = self.soft_wrap(line, width, break_words)
		return sub_lines

	# returns the cursor position in a wrapped document given its actual position in the raw document
	def get_wrapped_curpos(self, sublines, x):
		if(len(sublines) <= 1): return (0,x)

		i = 0
		vpos = -1
		cpos = x
		for l in sublines:
			if(cpos < len(l)):
				vpos = i
				break
			else:
				cpos -= len(l)
			i += 1

		return (vpos, cpos)

	# returns the position of the cursor on screen given its actual position in the document
	def get_rendered_pos(self, lines, width, hard_wrap, orig_pos, cum_lengths):
		wrapped_current_line = self.soft_wrap(lines[orig_pos.y], width, hard_wrap)
		offset_y, offset_x = self.get_wrapped_curpos(wrapped_current_line, orig_pos.x)
		y = cum_lengths[orig_pos.y] + offset_y
		x = offset_x
		rendered_curpos = CursorPosition(y, x)	
		return rendered_curpos

	# finds all text in the given document
	def find_all(self, s):
		self.ed.find_mode = True
		self.ed.highlighted_text = s
		self.ed.repaint()

	# cancels all highlights if any
	def cancel_find(self):
		self.ed.find_mode = False
		if(self.ed.highlighted_text != None):
			self.ed.highlighted_text = None
			self.ed.repaint()

	# moves cursor to next match
	def find_next(self, s):
		self.find_all(s)
		n = len(s)
		
		for y in range(self.ed.curpos.y, len(self.ed.buffer.lines)):
			start = 0
			if(y == self.ed.curpos.y): start = self.ed.curpos.x + 1
			x = self.ed.buffer.lines[y].find(s, start)
			if(x > -1):
				self.ed.curpos.y = y
				self.ed.curpos.x = x
				return

		for y in range(0, self.ed.curpos.y + 1):
			x = self.ed.buffer.lines[y].find(s)
			if(x > -1):
				self.ed.curpos.y = y
				self.ed.curpos.x = x
				return

	# moves cursor to previous match
	def find_previous(self, s):
		log("called find_prev")
		self.find_all(s)
		n = len(s)
		
		for y in range(self.ed.curpos.y, -1, -1):
			if(y == self.ed.curpos.y):
				x = self.ed.buffer.lines[y][0:self.ed.curpos.x].rfind(s)
			else:
				x = self.ed.buffer.lines[y].rfind(s)

			if(x > -1):
				self.ed.curpos.y = y
				self.ed.curpos.x = x
				return

		for y in range(len(self.ed.buffer.lines) - 1, self.ed.curpos.y - 1, -1):
			if(y == self.ed.curpos.y):
				x = self.ed.buffer.lines[y][0:self.ed.curpos.x].rfind(s)
			else:
				x = self.ed.buffer.lines[y].rfind(s)
			if(x > -1):
				self.ed.curpos.y = y
				self.ed.curpos.x = x
				return
		
	# replaces the first occurrence (after last find/replace operation)
	def replace_next(self, sfind, srep, do_update = True):
		n = len(sfind)
		line = self.ed.buffer.lines[self.ed.curpos.y]
		if(line[self.ed.curpos.x:self.ed.curpos.x+n] == sfind):
			prev = line[0:self.ed.curpos.x]
			next = line[self.ed.curpos.x+n:]
			self.ed.buffer.lines[self.ed.curpos.y] = prev + srep + next
			if(do_update): self.ed.buffer.major_update(self.ed.curpos, self.ed)
			self.find_next(sfind)
			return True
		
		return False

	def replace_all(self, sfind, srep):
		self.find_next(sfind)
		count = 0
		while(self.replace_next(sfind, srep, False)):
			count += 1		
		if(count > 0): self.ed.buffer.major_update(self.ed.curpos, self.ed, True)