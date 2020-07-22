# ---------------------------------------------------------------------------------------------
#  Copyright (c) Akash Nag. All rights reserved.
#  Licensed under the MIT License. See LICENSE.md in the project root for license information.
# ---------------------------------------------------------------------------------------------

# This module is a helper class for Editor

from ash.gui import *
from ash.gui.cursorPosition import *

class EditorUtility:
	def __init__(self, ed):
		self.ed = ed

	# delete the selected text
	def delete_selected_text(self):
		if(not self.ed.selection_mode): return
		start, end = self.ed.screen.get_selection_endpoints(self.ed.sel_start, self.ed.sel_end)
		del_text = ""

		if(start.y == end.y):
			sel_len = end.x - start.x
			del_text = self.ed.buffer.lines[start.y][start.x:end.x]
			if(len(del_text) > 0): self.ed.buffer.add_change(self.ed.curpos)
			self.ed.buffer.lines[start.y] = self.ed.buffer.lines[start.y][0:start.x] + self.ed.buffer.lines[start.y][end.x:]
			self.ed.curpos = copy.copy(start)
		else:
			del_text = self.ed.buffer.lines[start.y][start.x:] + "\n"
			if(len(del_text) > 0): self.ed.buffer.add_change(self.ed.curpos)
			
			# delete entire lines between selection start and end
			lc = end.y - start.y - 1
			while(lc > 0):
				del_text += self.ed.buffer.lines[start.y+1] + "\n"
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

		self.ed.curpos.x = max([0, self.ed.curpos.x])
		
		# turn off selection mode
		self.ed.selection_mode = False
		return del_text

	# returns the selected text
	def get_selected_text(self):
		if(not self.ed.selection_mode): return ""
		start, end = self.ed.screen.get_selection_endpoints(self.ed.sel_start, self.ed.sel_end)
		sel_text = ""

		if(start.y == end.y):
			sel_len = end.x - start.x
			sel_text = self.ed.buffer.lines[start.y][start.x:end.x]
		else:
			sel_text = self.ed.buffer.lines[start.y][start.x:] + "\n"
			for row in range(start.y+1, end.y):
				sel_text += self.ed.buffer.lines[row] + "\n"
			sel_text += self.ed.buffer.lines[end.y][0:end.x]

		return sel_text

	# returns the length of the selection (for showing in status bar)
	def get_selection_length_as_string(self):
		count = len(self.get_selected_text())
		if(count == 0):
			return ""
		else:
			return " {" + str(count) + "}"

	# increase indent of selected lines
	def shift_selection_right(self):
		start, end = self.ed.screen.get_selection_endpoints(self.ed.sel_start, self.ed.sel_end)
		for i in range(start.y, end.y+1):
			self.ed.buffer.lines[i] = "\t" + self.ed.buffer.lines[i]
		self.ed.curpos.x += 1
		self.ed.sel_start.x += 1
		self.ed.sel_end.x += 1
		
		return True

	# decrease indent of selected lines
	def shift_selection_left(self):
		start, end = self.ed.screen.get_selection_endpoints(self.ed.sel_start, self.ed.sel_end)

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
	
	# finds all text in the given document
	def find_all(self, s, match_case, whole_words, regex):
		self.ed.find_mode = (True if len(s) > 0 else False)
		self.ed.highlighted_text = (s if len(s) > 0 else None)
		self.ed.find_match_case = match_case
		self.ed.find_whole_words = whole_words
		self.ed.find_regex = regex
		self.ed.repaint()

	# cancels all highlights if any
	def cancel_find(self):
		self.ed.find_mode = False
		if(self.ed.highlighted_text != None):
			self.ed.highlighted_text = None
			self.ed.repaint()

	# moves cursor to next match
	def find_next(self, s, match_case, whole_words, regex):
		if(len(s) == 0): return

		lower_s = s.lower()
		self.find_all(s, match_case, whole_words, regex)
		n = len(s)
		
		for y in range(self.ed.curpos.y, len(self.ed.buffer.lines)):
			start = 0
			if(y == self.ed.curpos.y): start = self.ed.curpos.x + 1
			if(match_case):
				x = self.ed.buffer.lines[y].find(s, start)
			else:
				x = self.ed.buffer.lines[y].lower().find(lower_s, start)
			if(x > -1):
				self.ed.curpos.y = y
				self.ed.curpos.x = x
				return

		for y in range(0, self.ed.curpos.y + 1):
			if(match_case):
				x = self.ed.buffer.lines[y].find(s)
			else:
				x = self.ed.buffer.lines[y].lower().find(lower_s)
			if(x > -1):
				self.ed.curpos.y = y
				self.ed.curpos.x = x
				return

	# moves cursor to previous match
	def find_previous(self, s, match_case, whole_words, regex):
		if(len(s) == 0): return
		
		lower_s = s.lower()
		self.find_all(s, match_case, whole_words, regex)
		n = len(s)
		
		for y in range(self.ed.curpos.y, -1, -1):
			if(y == self.ed.curpos.y):
				portion = self.ed.buffer.lines[y][0:self.ed.curpos.x]
				if(match_case):
					x = portion.rfind(s)
				else:
					x = portion.lower().rfind(lower_s)
			else:
				portion = self.ed.buffer.lines[y]
				if(match_case):
					x = portion.rfind(s)
				else:
					x = portion.lower().rfind(lower_s)

			if(x > -1):
				self.ed.curpos.y = y
				self.ed.curpos.x = x
				return

		for y in range(len(self.ed.buffer.lines) - 1, self.ed.curpos.y - 1, -1):
			if(y == self.ed.curpos.y):
				portion = self.ed.buffer.lines[y][0:self.ed.curpos.x]
				if(match_case):
					x = portion.rfind(s)
				else:
					x = portion.lower().rfind(lower_s)
			else:
				portion = self.ed.buffer.lines[y]
				if(match_case):
					x = portion.rfind(s)
				else:
					x = portion.lower().rfind(lower_s)

			if(x > -1):
				self.ed.curpos.y = y
				self.ed.curpos.x = x
				return
		
	# replaces the first occurrence (after last find/replace operation)
	def replace_next(self, sfind, srep, match_case, whole_words, regex):
		n = len(sfind)
		line = self.ed.buffer.lines[self.ed.curpos.y]
		if(line[self.ed.curpos.x:self.ed.curpos.x+n] == sfind):
			prev = line[0:self.ed.curpos.x]
			next = line[self.ed.curpos.x+n:]
			self.ed.buffer.lines[self.ed.curpos.y] = prev + srep + next
			self.ed.buffer.major_update(self.ed.curpos, self.ed)
			self.find_next(sfind, match_case)
			return True
		
		return False

	def replace_all(self, sfind, srep, match_case, whole_words, regex):
		self.find_next(sfind, match_case)
		count = 0
		while(self.replace_next(sfind, srep, match_case)):
			count += 1		
		if(count > 0): self.ed.buffer.major_update(self.ed.curpos, self.ed, True)