# ---------------------------------------------------------------------------------------------
#  Copyright (c) Akash Nag. All rights reserved.
#  Licensed under the MIT License. See LICENSE.md in the project root for license information.
# ---------------------------------------------------------------------------------------------

# This module implements the key bindings for the text-editor widget

from ash.gui import *
from ash.utils.keyUtils import *
from ash.gui.cursorPosition import *

class EditorKeyHandler:
	def __init__(self, ed):
		self.ed = ed
	
	def handle_keys(self, ch):
		if(not KeyBindings.is_key(ch, "ADD_SLAVE_CURSOR")): self.cancel_multiple_cursors()

		if(KeyBindings.is_key(ch, "SELECT_ALL")):
			self.handle_select_all()
		elif(KeyBindings.is_key(ch, "COPY")):
			self.handle_copy()
		elif(KeyBindings.is_key(ch, "CUT")):
			return self.handle_cut()
		elif(KeyBindings.is_key(ch, "PASTE")):
			return self.handle_paste()
		elif(KeyBindings.is_key(ch, "SAVE")):
			try:
				self.handle_save()
			except:
				self.ed.parent.win.app.show_error("An error occurred while saving the file!")
		elif(KeyBindings.is_key(ch, "SAVE_AS")):
			try:
				self.ed.parent.win.app.dialog_handler.invoke_file_save_as(self.ed.buffer)
			except:
				self.ed.parent.win.app.show_error("An error occurred while saving the file!")
		elif(KeyBindings.is_key(ch, "SAVE_AND_CLOSE_EDITOR")):
			try:
				self.save_and_close()
			except:
				self.ed.parent.win.app.show_error("An error occurred while saving the file!")
		elif(KeyBindings.is_key(ch, "GOTO_LINE")):
			self.ed.parent.win.app.dialog_handler.invoke_go_to_line()
		elif(KeyBindings.is_key(ch, "OPEN_FILE")):
			self.ed.parent.win.app.dialog_handler.invoke_file_open()
		elif(KeyBindings.is_key(ch, "NEW_BUFFER")):
			self.ed.parent.win.app.dialog_handler.invoke_file_new()
		elif(KeyBindings.is_key(ch, "SHOW_FIND")):
			if(self.ed.find_mode):
				self.ed.find_mode = False
			else:
				self.ed.parent.win.app.dialog_handler.invoke_find()			
		elif(KeyBindings.is_key(ch, "SHOW_FIND_AND_REPLACE")):
			self.ed.parent.win.app.dialog_handler.invoke_find_and_replace()
		elif(KeyBindings.is_key(ch, "UNDO")):
			self.handle_undo()			
		elif(KeyBindings.is_key(ch, "REDO")):
			self.handle_redo()
		elif(KeyBindings.is_key(ch, "SHOW_PREFERENCES")):
			self.ed.parent.win.app.dialog_handler.invoke_set_preferences()
		elif(KeyBindings.is_key(ch, "DECODE_UNICODE")):
			self.ed.buffer.decode_unicode()
			return True
		elif(KeyBindings.is_key(ch, "CANCEL_MULTICURSOR_MODE")):
			self.cancel_multiple_cursors()
		elif(KeyBindings.is_key(ch, "ADD_SLAVE_CURSOR")):
			self.add_slave_cursor()

		return False

	def save_and_close(self):
		self.handle_save()
		if(self.ed.buffer.filename != None): self.ed.parent.win.app.dialog_handler.invoke_quit()

	# handle the 4 arrow keys
	def handle_arrow_keys(self, ch):
		self.cancel_multiple_cursors()

		if(KeyBindings.is_key(ch, "MOVE_CURSOR_LEFT")):
			self.ed.curpos = self.ed.screen.get_curpos_after_move_left(self.ed.curpos, self.ed.tab_size, self.ed.word_wrap, self.ed.hard_wrap)
		elif(KeyBindings.is_key(ch, "MOVE_CURSOR_RIGHT")):
			self.ed.curpos = self.ed.screen.get_curpos_after_move_right(self.ed.curpos, self.ed.tab_size, self.ed.word_wrap, self.ed.hard_wrap)			
		elif(KeyBindings.is_key(ch, "MOVE_CURSOR_DOWN")):
			self.ed.curpos = self.ed.screen.get_curpos_after_move_down(self.ed.curpos, self.ed.tab_size, self.ed.word_wrap, self.ed.hard_wrap)			
		elif(KeyBindings.is_key(ch, "MOVE_CURSOR_UP")):
			self.ed.curpos = self.ed.screen.get_curpos_after_move_up(self.ed.curpos, self.ed.tab_size, self.ed.word_wrap, self.ed.hard_wrap)
			
		self.ed.selection_mode = False		# turn off selection mode

	
	# handles Ctrl+Arrow key combinations
	# behaviour: move to the next/previous separator position
	def handle_ctrl_arrow_keys(self, ch):
		self.cancel_multiple_cursors()

		if(KeyBindings.is_key(ch, "MOVE_CURSOR_TO_PREVIOUS_WORD")):
			# previous-word left
			if(self.ed.curpos.x == 0):
				beep()
			else:
				for i in range(self.ed.curpos.x-1, -1, -1):
					c = self.ed.buffer.lines[self.ed.curpos.y][i]
					if(c in self.ed.separators):
						self.ed.curpos.x = i						
						return
				self.ed.curpos.x = 0
		elif(KeyBindings.is_key(ch, "MOVE_CURSOR_TO_NEXT_WORD")):
			# next-word right
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
		self.cancel_multiple_cursors()

		if(not self.ed.selection_mode):
			self.ed.selection_mode = True
			self.ed.sel_start = copy.copy(self.ed.curpos)
		
		if(KeyBindings.is_key(ch, "SELECT_CHARACTER_LEFT")):
			self.ed.curpos = self.ed.screen.get_curpos_after_move_left(self.ed.curpos, self.ed.tab_size, self.ed.word_wrap, self.ed.hard_wrap)
		elif(KeyBindings.is_key(ch, "SELECT_CHARACTER_RIGHT")):
			self.ed.curpos = self.ed.screen.get_curpos_after_move_right(self.ed.curpos, self.ed.tab_size, self.ed.word_wrap, self.ed.hard_wrap)			
		elif(KeyBindings.is_key(ch, "SELECT_LINE_BELOW")):
			self.ed.curpos = self.ed.screen.get_curpos_after_move_down(self.ed.curpos, self.ed.tab_size, self.ed.word_wrap, self.ed.hard_wrap)			
		elif(KeyBindings.is_key(ch, "SELECT_LINE_ABOVE")):
			self.ed.curpos = self.ed.screen.get_curpos_after_move_up(self.ed.curpos, self.ed.tab_size, self.ed.word_wrap, self.ed.hard_wrap)
		
		self.ed.sel_end = copy.copy(self.ed.curpos)

	# handles DEL key press: delete a character to the right
	# of the cursor, or deletes the selected text
	def handle_delete_key(self, ch):
		if(self.ed.selection_mode):
			self.cancel_multiple_cursors()
			self.ed.utility.delete_selected_text()
			return True
		
		text = self.ed.buffer.lines[self.ed.curpos.y]
		clen = len(text)
		col = self.ed.curpos.x

		if(self.ed.curpos.y == len(self.ed.buffer.lines)-1 and col == clen):
			beep()
			return False
		
		if(col == clen):
			self.cancel_multiple_cursors()
			ntext = self.ed.buffer.lines[self.ed.curpos.y + 1]
			self.ed.buffer.lines.pop(self.ed.curpos.y + 1)
			self.ed.buffer.lines[self.ed.curpos.y] += ntext
		else:
			left = text[0:col] if col > 0 else ""
			right = text[col+1:] if col < clen-1 else ""
			self.ed.buffer.lines[self.ed.curpos.y] = left + right

			for sc in self.ed.slave_cursors:
				text = self.ed.buffer.lines[sc.y]
				clen = len(text)
				col = sc.x
				left = text[0:col] if col > 0 else ""
				right = text[col+1:] if col < clen-1 else ""
				self.ed.buffer.lines[sc.y] = left + right
				
		return True
	
	# handles backspace key: deletes the character to the left of the
	# cursor, or deletes the selected text
	def handle_backspace_key(self, ch):
		if(self.ed.selection_mode):
			self.cancel_multiple_cursors()
			self.ed.utility.delete_selected_text()						
			return True		

		text = self.ed.buffer.lines[self.ed.curpos.y]
		col = self.ed.curpos.x

		if(col == 0 and self.ed.curpos.y == 0):
			beep()
			return False

		if(col == 0):
			self.cancel_multiple_cursors()
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

			for sc in self.ed.slave_cursors:
				text = self.ed.buffer.lines[sc.y]
				col = sc.x
				left = text[0:col-1] if col > 1 else ""
				right = text[col:] if col < len(text) else ""
				self.ed.buffer.lines[sc.y] = left + right
				sc.x -= 1
		
		return True

	# handles HOME and END keys
	def handle_home_end_keys(self, ch):
		self.cancel_multiple_cursors()
		self.ed.selection_mode = False

		if(KeyBindings.is_key(ch, "MOVE_CURSOR_TO_LINE_START")):
			self.ed.curpos = self.ed.screen.get_curpos_after_move_home(self.ed.curpos, self.ed.tab_size, self.ed.word_wrap, self.ed.hard_wrap)
		elif(KeyBindings.is_key(ch, "MOVE_CURSOR_TO_LINE_END")):
			self.ed.curpos = self.ed.screen.get_curpos_after_move_end(self.ed.curpos, self.ed.tab_size, self.ed.word_wrap, self.ed.hard_wrap)
		
	# handles Shift+Home and Shift+End keys
	def handle_shift_home_end_keys(self, ch):
		self.cancel_multiple_cursors()
		if(not self.ed.selection_mode):
			self.ed.selection_mode = True
			self.ed.sel_start = copy.copy(self.ed.curpos)
		
		if(KeyBindings.is_key(ch, "SELECT_TILL_LINE_START")):
			self.ed.curpos = self.ed.screen.get_curpos_after_move_home(self.ed.curpos, self.ed.tab_size, self.ed.word_wrap, self.ed.hard_wrap)
		elif(KeyBindings.is_key(ch, "SELECT_TILL_LINE_END")):
			self.ed.curpos = self.ed.screen.get_curpos_after_move_end(self.ed.curpos, self.ed.tab_size, self.ed.word_wrap, self.ed.hard_wrap)

		self.ed.sel_end = copy.copy(self.ed.curpos)

	# handles TAB/Ctrl+I and Shift+TAB keys
	# in selection mode: increase / decrease indent
	def handle_tab_keys(self, ch):
		self.cancel_multiple_cursors()
		if(self.ed.selection_mode):
			if(KeyBindings.is_key(ch, "INSERT_TAB")):
				return self.ed.shift_selection_right()
			elif(KeyBindings.is_key(ch, "DECREASE_INDENT")):
				return self.ed.shift_selection_left()

		col = self.ed.curpos.x
		text = self.ed.buffer.lines[self.ed.curpos.y]

		if(KeyBindings.is_key(ch, "INSERT_TAB")):
			left = text[0:col] if col > 0 else ""
			right = text[col:] if len(text) > 0 else ""
			self.ed.buffer.lines[self.ed.curpos.y] = left + "\t" + right
			self.ed.curpos.x += 1
		elif(KeyBindings.is_key(ch, "DECREASE_INDENT")):
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
	def handle_newline(self):
		self.cancel_multiple_cursors()
		if(self.ed.selection_mode): self.ed.utility.delete_selected_text()

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
	def handle_printable_character(self, ch):
		if(self.ed.selection_mode): self.cancel_multiple_cursors()
		sch = str(chr(ch))
		
		if(self.ed.auto_close):
			# if parenthesis or quotes, put selected-text in between them
			open = "([{\'\"\`"
			close = ")]}\'\"\`"

			pos = open.find(sch)
			if(pos > -1):
				if(self.ed.selection_mode):
					del_text = self.ed.utility.delete_selected_text()
					old_clipboard = clipboard.paste()
					del_text = open[pos] + del_text + close[pos]
					clipboard.copy(del_text)
					self.handle_paste()
					clipboard.copy(old_clipboard)
					return True
				else:
					sch = open[pos] + close[pos]

		if(self.ed.selection_mode): del_text = self.ed.utility.delete_selected_text()

		text = self.ed.buffer.lines[self.ed.curpos.y]
		col = self.ed.curpos.x
		left = text[0:col] if col > 0 else ""
		right = text[col:] if len(text) > 0 else ""
		
		self.ed.buffer.lines[self.ed.curpos.y] = left + sch + right
		self.ed.curpos.x += 1

		for sc in self.ed.slave_cursors:
			text = self.ed.buffer.lines[sc.y]
			col = sc.x
			left = text[0:col] if col > 0 else ""
			right = text[col:] if len(text) > 0 else ""

			self.ed.buffer.lines[sc.y] = left + sch + right
			sc.x += 1

		return True
			
	# handles the PGUP and PGDOWN keys
	def handle_page_navigation_keys(self, ch):
		self.cancel_multiple_cursors()
		h = self.ed.height
		nlen = len(self.ed.buffer.lines)
		if(KeyBindings.is_key(ch, "MOVE_TO_PREVIOUS_PAGE")):
			# page up
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
		elif(KeyBindings.is_key(ch, "MOVE_TO_NEXT_PAGE")):
			# page down
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
		self.cancel_multiple_cursors()
		if(self.ed.selection_mode): self.ed.selection_mode = False

		if(KeyBindings.is_key(ch, "MOVE_CURSOR_TO_DOCUMENT_START")):
			self.ed.curpos.y = 0
			self.ed.curpos.x = 0
		elif(KeyBindings.is_key(ch, "MOVE_CURSOR_TO_DOCUMENT_END")):
			self.ed.curpos.y = len(self.ed.buffer.lines)-1
			self.ed.curpos.x = len(self.ed.buffer.lines[self.ed.curpos.y])
	
	# handles the Shift + PGUP / PGDOWN keys
	def handle_shift_page_navigation_keys(self, ch):
		self.cancel_multiple_cursors()
		if(not self.ed.selection_mode):
			self.ed.selection_mode = True
			self.ed.sel_start = copy.copy(self.ed.curpos)
		
		h = self.ed.height
		nlen = len(self.ed.buffer.lines)
		if(KeyBindings.is_key(ch, "SELECT_PAGE_ABOVE")):
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
		elif(KeyBindings.is_key(ch, "SELECT_PAGE_BELOW")):
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
		self.cancel_multiple_cursors()
		self.ed.buffer.do_undo()
		self.ed.recompute()
		self.ed.parent.bottom_up_repaint()

	def handle_redo(self):
		self.cancel_multiple_cursors()
		self.ed.buffer.do_redo()
		self.ed.recompute()
		self.ed.parent.bottom_up_repaint()

	def handle_save(self):
		if(not self.ed.buffer.save_status):
			if(self.ed.buffer.filename != None):
				self.ed.buffer.write_to_disk()
			else:
				self.ed.parent.win.app.dialog_handler.invoke_file_save_as(self.ed.buffer)

	def handle_select_all(self):
		self.cancel_multiple_cursors()
		nlen = len(self.ed.buffer.lines)
		self.ed.selection_mode = True
		self.ed.sel_start.y = 0
		self.ed.sel_start.x = 0
		self.ed.sel_end.y = nlen-1
		self.ed.sel_end.x = len(self.ed.buffer.lines[nlen-1])

	def handle_select_line(self):
		self.cancel_multiple_cursors()
		self.ed.selection_mode = True
		self.ed.curpos.x = len(self.ed.buffer.lines[self.ed.curpos.y])
		self.ed.sel_start.y = self.ed.curpos.y
		self.ed.sel_start.x = 0
		self.ed.sel_end.y = self.ed.curpos.y
		self.ed.sel_end.x = self.ed.curpos.x

	def handle_copy(self):
		self.cancel_multiple_cursors()
		if(not self.ed.selection_mode): return
		sel_text = self.ed.get_selected_text()
		clipboard.copy(sel_text)

	def handle_cut(self):
		self.cancel_multiple_cursors()
		if(not self.ed.selection_mode): return False
		del_text = self.ed.utility.delete_selected_text()
		clipboard.copy(del_text)
		self.ed.recompute()
		return True
			
	def handle_paste(self):
		self.cancel_multiple_cursors()
		whole = clipboard.paste()
		if(len(whole) == 0): return False

		data = whole.splitlines()
		if(self.ed.selection_mode): self.ed.utility.delete_selected_text()
		
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

		self.ed.recompute()
		return True

	def add_slave_cursor(self):
		if(len(self.ed.slave_cursors) == 0):
			last = self.ed.curpos
		else:
			last = self.ed.slave_cursors[-1]
		
		if(last.y >= len(self.ed.buffer.lines)-1): return
		if(last.x > len(self.ed.buffer.lines[last.y+1])): return

		self.ed.slave_cursors.append( CursorPosition(last.y + 1, last.x) )

	def cancel_multiple_cursors(self):
		self.ed.slave_cursors = list()