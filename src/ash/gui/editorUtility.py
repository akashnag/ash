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

	# implements search
	def find_next(self, str):
		pass

	def find_previous(self, str):
		pass

	# replaces the first occurrence (after last find/replace operation)
	def replace(self, strf, strr):
		pass

	def replace_all(self, strf, strr):
		pass