# ---------------------------------------------------------------------------------------------
#  Copyright (c) Akash Nag. All rights reserved.
#  Licensed under the MIT License. See LICENSE.md in the project root for license information.
# ---------------------------------------------------------------------------------------------

# This module implements the key bindings for the text-editor widget

from ash.gui import *
from ash.formatting.formatting import *
from ash.core.utils import *

class EditorKeyHandler:
	def __init__(self, ed):
		self.ed = ed
	
	def handle_ctrl_and_func_keys(self, ch):
		if(is_ctrl(ch, "A")):
			self.handle_select_all()
		elif(is_ctrl(ch, "C")):
			self.handle_copy()
		elif(is_ctrl(ch, "X")):
			return self.handle_cut()
		elif(is_ctrl(ch, "V")):
			return self.handle_paste()
		elif(is_ctrl(ch, "S")):
			self.handle_save()
		elif(is_ctrl(ch, "G")):
			self.ed.parent.app.dialog_handler.invoke_go_to_line()
		elif(is_ctrl(ch, "O")):
			self.ed.parent.app.dialog_handler.invoke_file_open()
		elif(is_ctrl(ch, "N")):
			self.ed.parent.app.dialog_handler.invoke_file_new()
		elif(is_ctrl(ch, "F")):
			self.ed.parent.app.dialog_handler.invoke_find()			
		elif(is_ctrl(ch, "H")):
			self.ed.parent.app.dialog_handler.invoke_find_and_replace()
		elif(is_ctrl(ch, "T")):
			self.ed.parent.app.dialog_handler.invoke_file_print()
		elif(is_ctrl(ch, "Z")):
			self.handle_undo()
		elif(is_ctrl(ch, "Y")):
			self.handle_redo()
		elif(is_ctrl(ch, "P")):
			self.ed.parent.app.dialog_handler.invoke_set_preferences()

		return False

	# handle the 4 arrow keys
	def handle_arrow_keys(self, ch):
		row = self.ed.curpos.y
		col = self.ed.curpos.x
		clen = len(self.ed.buffer.lines[row])
		nlen = len(self.ed.buffer.lines)
		
		if(ch == curses.KEY_LEFT):
			if(row == 0 and col == 0):
				beep()
			elif(col == 0):
				self.ed.curpos.y -= 1
				self.ed.curpos.x = len(self.ed.buffer.lines[row-1])
			else:
				# move cursor back only if selection-mode is inactive
				if(not self.ed.selection_mode): self.ed.curpos.x -= 1
		elif(ch == curses.KEY_RIGHT):
			if(row == nlen-1 and col == clen):
				beep()
			elif(col == clen):
				self.ed.curpos.y += 1
				self.ed.curpos.x = 0
			else:
				if(not self.ed.selection_mode):
					self.ed.curpos.x += 1
				else:
					# move cursor to the end of selection
					start, end = self.ed.get_selection_endpoints()
					self.ed.curpos.y = end.y
					self.ed.curpos.x = end.x
		elif(ch == curses.KEY_DOWN):
			if(row == nlen-1):
				beep()
			else:
				if(self.ed.curpos.x > len(self.ed.buffer.lines[row+1])):
					# cannot preserve column, so move to end
					self.ed.curpos.x = len(self.ed.buffer.lines[row+1])
				self.ed.curpos.y += 1
		elif(ch == curses.KEY_UP):
			if(row == 0):
				beep()
			else:
				if(self.ed.curpos.x > len(self.ed.buffer.lines[row-1])):
					# cannot preserve column, so move to end
					self.ed.curpos.x = len(self.ed.buffer.lines[row-1])
				self.ed.curpos.y -= 1

		self.ed.selection_mode = False		# turn off selection mode

		# ensure cursor position does not exceed editor/document limits
		self.ed.curpos.x = min([self.ed.curpos.x, len(self.ed.buffer.lines[self.ed.curpos.y])])
		self.ed.curpos.x = max(0, self.ed.curpos.x)
		self.ed.curpos.y = min([self.ed.curpos.y, len(self.ed.buffer.lines)-1])
		self.ed.curpos.y = max(0, self.ed.curpos.y)

	
	# handles Ctrl+Arrow key combinations
	# behaviour: move to the next/previous separator position
	def handle_ctrl_arrow_keys(self, ch):
		if(is_ctrl_arrow(ch, "LEFT")):
			if(self.ed.curpos.x == 0):
				beep()
			else:
				for i in range(self.ed.curpos.x-1, -1, -1):
					c = self.ed.buffer.lines[self.ed.curpos.y][i]
					if(c in self.ed.separators):
						self.ed.curpos.x = i						
						return
				self.ed.curpos.x = 0
		elif(is_ctrl_arrow(ch, "RIGHT")):
			nlen = len(self.ed.buffer.lines[self.ed.curpos.y])
			if(self.ed.curpos.x == nlen):
				beep()
			else:
				for i in range(self.ed.curpos.x+1, nlen):
					c = self.ed.buffer.lines[self.ed.curpos.y][i]
					if(c in self.ed.separators):
						self.ed.curpos.x = i					
						return
				self.ed.curpos.x = nlen

	# handles Shift+Arrow key combinations
	# behaviour: initiates/extends text selection
	def handle_shift_arrow_keys(self, ch):
		row = self.ed.curpos.y
		col = self.ed.curpos.x
		nlen = len(self.ed.buffer.lines)
		clen = len(self.ed.buffer.lines[row])

		if(not self.ed.selection_mode):
			self.ed.selection_mode = True
			self.ed.sel_start = copy.copy(self.ed.curpos)
		
		if(ch == curses.KEY_SLEFT):
			if(row == 0 and col == 0):
				beep()
			elif(col == 0):
				self.ed.curpos.y -= 1
				self.ed.curpos.x = len(self.ed.buffer.lines[row-1])
			else:
				self.ed.curpos.x -= 1
		elif(ch == curses.KEY_SRIGHT):
			if(row == nlen-1 and col == clen):
				beep()
			elif(col == clen):
				self.ed.curpos.y += 1
				self.ed.curpos.x = 0
			else:
				self.ed.curpos.x += 1
		elif(ch == curses.KEY_SF):
			if(row == nlen-1):
				beep()
			else:
				if(self.ed.curpos.x > len(self.ed.buffer.lines[row+1])):
					# cannot preserve column
					self.ed.curpos.x = len(self.ed.buffer.lines[row+1])
				self.ed.curpos.y += 1
		elif(ch == curses.KEY_SR):
			if(row == 0):
				beep()
			else:
				if(self.ed.curpos.x > len(self.ed.buffer.lines[row-1])):
					# cannot preserve column
					self.ed.curpos.x = len(self.ed.buffer.lines[row-1])
				self.ed.curpos.y -= 1

		# ensure cursor does not exceed bounds
		self.ed.curpos.x = min([self.ed.curpos.x, len(self.ed.buffer.lines[self.ed.curpos.y])])
		self.ed.curpos.x = max(0, self.ed.curpos.x)
		self.ed.curpos.y = min([self.ed.curpos.y, len(self.ed.buffer.lines)-1])
		self.ed.curpos.y = max(0, self.ed.curpos.y)
		self.ed.sel_end = copy.copy(self.ed.curpos)

	# handles DEL key press: delete a character to the right
	# of the cursor, or deletes the selected text
	def handle_delete_key(self, ch):
		if(self.ed.selection_mode):
			self.ed.delete_selected_text()
			return True
		
		text = self.ed.buffer.lines[self.ed.curpos.y]
		clen = len(text)
		col = self.ed.curpos.x

		if(self.ed.curpos.y == len(self.ed.buffer.lines)-1 and col == clen):
			beep()
			return False
		
		if(col == clen):
			ntext = self.ed.buffer.lines[self.ed.curpos.y + 1]
			self.ed.buffer.lines.pop(self.ed.curpos.y + 1)
			self.ed.buffer.lines[self.ed.curpos.y] += ntext
		else:
			left = text[0:col] if col > 0 else ""
			right = text[col+1:] if col < len(text)-1 else ""
			self.ed.buffer.lines[self.ed.curpos.y] = left + right
				
		return True
	
	# handles backspace key: deletes the character to the left of the
	# cursor, or deletes the selected text
	def handle_backspace_key(self, ch):
		if(self.ed.selection_mode):
			self.ed.delete_selected_text()						
			return True		

		text = self.ed.buffer.lines[self.ed.curpos.y]
		col = self.ed.curpos.x

		if(col == 0 and self.ed.curpos.y == 0):
			beep()
			return False

		if(col == 0):
			self.ed.buffer.lines.pop(self.ed.curpos.y)
			temp = len(self.ed.buffer.lines[self.ed.curpos.y-1])
			self.ed.buffer.lines[self.ed.curpos.y - 1] += text
			self.ed.curpos.x = temp
			self.ed.curpos.y -= 1
		else:
			left = text[0:col-1] if col > 1 else ""
			right = text[col:] if col < len(text) else ""
			self.ed.buffer.lines[self.ed.curpos.y] = left + right
			self.ed.curpos.x -= 1		
		
		return True

	# handles HOME and END keys
	def handle_home_end_keys(self, ch):
		self.ed.selection_mode = False

		if(self.ed.word_wrap):
			if(ch == curses.KEY_HOME):
				self.ed.curpos.x = self.ed.col_spans[self.ed.rendered_curpos.y][0]
			elif(ch == curses.KEY_END):
				self.ed.curpos.x = self.ed.col_spans[self.ed.rendered_curpos.y][1]
		else:
			if(ch == curses.KEY_HOME):
				# toggle between beginning of line and beginning of indented-code
				if(self.ed.curpos.x == 0):
					self.ed.curpos.x = len(self.ed.get_leading_whitespaces(self.ed.curpos.y))
				else:
					self.ed.curpos.x = 0
			elif(ch == curses.KEY_END):
				self.ed.curpos.x = len(self.ed.buffer.lines[self.ed.curpos.y])

	# handles Shift+Home and Shift+End keys
	def handle_shift_home_end_keys(self, ch):
		if(not self.ed.selection_mode):
			self.ed.selection_mode = True
			self.ed.sel_start = copy.copy(self.ed.curpos)
		
		if(ch == curses.KEY_SHOME):
			self.ed.curpos.x = 0
		elif(ch == curses.KEY_SEND):
			self.ed.curpos.x = len(self.ed.buffer.lines[self.ed.curpos.y])
				
		self.ed.sel_end = copy.copy(self.ed.curpos)

	# handles TAB/Ctrl+I and Shift+TAB keys
	# in selection mode: increase / decrease indent
	def handle_tab_keys(self, ch):
		if(self.ed.selection_mode):
			if(is_tab(ch)):
				return self.ed.shift_selection_right()
			elif(ch == curses.KEY_BTAB):
				return self.ed.shift_selection_left()

		col = self.ed.curpos.x
		text = self.ed.buffer.lines[self.ed.curpos.y]

		if(is_tab(ch)):
			left = text[0:col] if col > 0 else ""
			right = text[col:] if len(text) > 0 else ""
			self.ed.buffer.lines[self.ed.curpos.y] = left + "\t" + right
			self.ed.curpos.x += 1
		elif(ch == curses.KEY_BTAB):
			if(col == 0):
				beep()
				return False
			elif(col == len(self.ed.get_leading_whitespaces(self.ed.curpos.y))):
				left = text[0:col-1] if col > 1 else ""
				right = text[col:] if col < len(text) else ""
				self.ed.buffer.lines[self.ed.curpos.y] = left + right
				self.ed.curpos.x -= 1
			else:
				beep()
				return False
		
		return True
		
	# handles ENTER / Ctrl+J
	def handle_newline(self, ch):
		if(self.ed.selection_mode): self.ed.delete_selected_text()

		text = self.ed.buffer.lines[self.ed.curpos.y]
		col = self.ed.curpos.x
		left = text[0:col] if col > 0 else ""
		right = text[col:] if len(text) > 0 else ""
		whitespaces = self.ed.get_leading_whitespaces(self.ed.curpos.y)
		right = whitespaces + right
		self.ed.buffer.lines[self.ed.curpos.y] = left

		if(len(self.ed.buffer.lines) == self.ed.curpos.y + 1):
			self.ed.buffer.lines.append(right)
		else:
			self.ed.buffer.lines.insert(self.ed.curpos.y + 1, right)
		
		self.ed.curpos.y += 1
		self.ed.curpos.x = len(whitespaces)
		
		return True
			
	# handles printable characters in the charset
	# TO DO: add support for Unicode
	def handle_printable_character(self, ch):
		sch = str(chr(ch))
		
		if(self.ed.selection_mode): 
			del_text = self.ed.delete_selected_text()

			# if parenthesis or quotes, put selected-text in between them
			open = "([{\'\"\`"
			close = ")]}\'\"\`"

			pos = open.find(sch)
			if(pos > -1):
				old_clipboard = clipboard.paste()
				del_text = open[pos] + del_text + close[pos]
				clipboard.copy(del_text)
				self.handle_paste()
				clipboard.copy(old_clipboard)
				return True

		text = self.ed.buffer.lines[self.ed.curpos.y]
		col = self.ed.curpos.x
		left = text[0:col] if col > 0 else ""
		right = text[col:] if len(text) > 0 else ""
		self.ed.buffer.lines[self.ed.curpos.y] = left + sch + right
		self.ed.curpos.x += 1		

		return (True if sch in self.ed.separators else False)
			
	# handles the PGUP and PGDOWN keys
	def handle_page_navigation_keys(self, ch):
		h = self.ed.height
		nlen = len(self.ed.buffer.lines)
		if(ch == curses.KEY_PPAGE):			# pg-up
			if(self.ed.curpos.y == 0):
				if(self.ed.curpos.x == 0):
					beep()
				else:
					self.ed.curpos.x = 0
					return
			elif(self.ed.curpos.y <= h):
				self.ed.curpos.y = 0
			else:
				self.ed.curpos.y -= h-1
			self.ed.curpos.x = 0
		elif(ch == curses.KEY_NPAGE):		# pg-down
			if(self.ed.curpos.y == nlen-1):
				if(self.ed.curpos.x == len(self.ed.buffer.lines[nlen-1])):
					beep()
				else:
					self.ed.curpos.x = len(self.ed.buffer.lines[nlen-1])
					return
			elif(nlen - self.ed.curpos.y <= h):
				self.ed.curpos.y = nlen-1
			else:
				self.ed.curpos.y += h-1
			self.ed.curpos.x = 0

	# handles the Ctrl + HOME / END keys
	def handle_ctrl_home_end_keys(self, ch):
		if(self.ed.selection_mode): self.ed.selection_mode = False

		if(is_keyname(ch, "HOM5")):		# Ctrl+Home
			self.ed.curpos.y = 0
			self.ed.curpos.x = 0
		elif(is_keyname(ch, "END5")):	# Ctrl+End
			self.ed.curpos.y = len(self.ed.buffer.lines)-1
			self.ed.curpos.x = len(self.ed.buffer.lines[self.ed.curpos.y])
	
	# handles the Shift + PGUP / PGDOWN keys
	def handle_shift_page_navigation_keys(self, ch):
		if(not self.ed.selection_mode):
			self.ed.selection_mode = True
			self.ed.sel_start = copy.copy(self.ed.curpos)
		
		h = self.ed.height
		nlen = len(self.ed.buffer.lines)
		if(ch == curses.KEY_SPREVIOUS):			# Shift + pg-up
			if(self.ed.curpos.y == 0):
				if(self.ed.curpos.x == 0):
					beep()
				else:
					self.ed.curpos.x = 0
					self.ed.sel_end = copy.copy(self.ed.curpos)
					return
			elif(self.ed.curpos.y <= h):
				self.ed.curpos.y = 0
			else:
				self.ed.curpos.y -= h-1
			self.ed.curpos.x = 0
			self.ed.sel_end = copy.copy(self.ed.curpos)
		elif(ch == curses.KEY_SNEXT):		# Shift + pg-down
			if(self.ed.curpos.y == nlen-1):
				if(self.ed.curpos.x == len(self.ed.buffer.lines[nlen-1])):
					beep()
				else:
					self.ed.curpos.x = len(self.ed.buffer.lines[nlen-1])
					self.ed.sel_end = copy.copy(self.ed.curpos)
					return
			elif(nlen - self.ed.curpos.y <= h):
				self.ed.curpos.y = nlen-1
			else:
				self.ed.curpos.y += h-1
			self.ed.curpos.x = 0
			self.ed.sel_end = copy.copy(self.ed.curpos)
		
	def handle_undo(self):
		hdata = self.ed.buffer.history.undo()
		if(hdata == None):
			beep()
		else:
			self.ed.render_data_to_lines(hdata.data, False)
			self.ed.curpos = copy.copy(hdata.curpos)

	def handle_redo(self):
		hdata = self.ed.buffer.history.redo()
		if(hdata == None):
			beep()
		else:
			self.ed.render_data_to_lines(hdata.data, False)
			self.ed.curpos = copy.copy(hdata.curpos)

	def handle_save(self):
		log("Ctrl+S pressed")
		if(not self.ed.buffer.save_status):
			if(self.ed.buffer.filename != None):
				self.ed.buffer.write_to_disk()
			else:
				self.ed.parent.app.dialog_handler.invoke_file_save_as(self.ed.buffer)

	def handle_select_all(self):
		nlen = len(self.ed.buffer.lines)
		self.ed.selection_mode = True
		self.ed.sel_start.y = 0
		self.ed.sel_start.x = 0
		self.ed.sel_end.y = nlen-1
		self.ed.sel_end.x = len(self.ed.buffer.lines[nlen-1])

	def handle_copy(self):
		if(not self.ed.selection_mode): return
		sel_text = self.ed.get_selected_text()
		clipboard.copy(sel_text)

	def handle_cut(self):
		if(not self.ed.selection_mode): return False
		del_text = self.ed.delete_selected_text()
		clipboard.copy(del_text)
		return True
			
	def handle_paste(self):
		whole = clipboard.paste()
		if(len(whole) == 0): return False

		data = whole.splitlines()
		if(self.ed.selection_mode): self.ed.delete_selected_text()
		
		n = len(data)
		row = self.ed.curpos.y
		text = self.ed.buffer.lines[row]
		col = self.ed.curpos.x
		left = text[0:col] if col > 0 else ""
		right = text[col:] if len(text) > 0 else ""
			
		if(n == 1):
			self.ed.buffer.lines[row] = left + data[0] + right
			self.ed.curpos.x += len(data[0])
		elif(n == 2):
			self.ed.buffer.lines[row] = left + data[0]
			self.ed.buffer.lines.insert(row+1, data[1] + right)
			self.ed.curpos.y += 1
			self.ed.curpos.x = len(data[1])
		elif(n > 2):
			self.ed.buffer.lines[row] = left + data[0]
			self.ed.buffer.lines.insert(row+1, data[n-1] + right)
			for i in range(n-2, 0, -1):
				self.ed.buffer.lines.insert(row+1, data[i])

		return True