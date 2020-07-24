# ---------------------------------------------------------------------------------------------
#  Copyright (c) Akash Nag. All rights reserved.
#  Licensed under the MIT License. See LICENSE.md in the project root for license information.
# ---------------------------------------------------------------------------------------------

# This module implements the TextField widget

from ash.gui import *

class TextField(Widget):
	def __init__(self, parent, y, x, width, initial_text = "", numeric = False, maxlen = -1, callback = None):
		super().__init__(WIDGET_TYPE_TEXTFIELD)
		self.y = y
		self.x = x
		self.height = 1
		self.width = width
		self.theme = gc("formfield")
		self.text = initial_text
		self.curpos = len(self.text)
		self.parent = parent
		self.numeric = numeric
		self.maxlen = maxlen
		self.callback = callback
		self.focus_theme = gc("formfield-focussed")
		self.is_in_focus = False

		self.charset = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789"
		self.charset += "~`!@#$%^&*()-_=+\\|[{]};:\'\",<.>/? "			
		self.numeric_charset = "-.0123456789"

		self.start = 0
		self.end = min([self.width, len(self.text)])
		self.selection_mode = False
		self.sel_start = 0
		self.sel_end = 0

		self.focus()
	
	# set the text to be displayed
	def set_text(self, text):
		self.text = text
		self.start = 0
		self.end = min([self.width, len(self.text)])
		self.curpos = len(text)
		self.repaint()
	
	# when focus received
	def focus(self):
		self.is_in_focus = True
		self.repaint()
		curses.curs_set(True)		

	# when focus lost
	def blur(self):
		self.is_in_focus = False
		curses.curs_set(False)
		self.repaint()

	# Delete the selected text
	def delete_selected_text(self):
		if(not self.selection_mode): return
		if(self.sel_start == self.sel_end): return
		
		if(self.sel_start > self.sel_end):
			sel_start, sel_end = self.sel_end, self.sel_start
		else:
			sel_start, sel_end = self.sel_start, self.sel_end

		del_text = self.text[sel_start:sel_end]
		if(self.curpos >= sel_start and self.curpos < sel_end):
			self.curpos = sel_start
		elif(self.curpos >= sel_end):
			self.curpos -= len(del_text)

		self.text = self.text[0:sel_start] + self.text[sel_end:]
		self.selection_mode = False
		return del_text

	# Handles backspace key
	def handle_backspace(self):
		if(self.selection_mode):
			self.delete_selected_text()
			return

		if(self.curpos > 0):
			self.text = (self.text[0:self.curpos-1] if self.curpos > 1 else "") + (self.text[self.curpos:] if self.curpos < len(self.text) else "")
			self.curpos -= 1
		else:
			beep()

	# Handles Del key
	def handle_delete(self):
		if(self.selection_mode):
			self.delete_selected_text()
			return

		if(self.curpos == len(self.text)):
			beep()
		else:
			self.text = (self.text[0:self.curpos] if self.curpos > 0 else "") + (self.text[self.curpos+1:] if self.curpos < len(self.text)-1 else "")

	# handles LeftArrow/RightArrow
	def handle_arrow_keys(self, ch):
		if(KeyBindings.is_key(ch, "MOVE_CURSOR_LEFT")):
			# KEY LEFT
			self.selection_mode = False
			if(self.curpos > 0): 
				self.curpos -= 1
			else:
				beep()
		elif(KeyBindings.is_key(ch, "MOVE_CURSOR_RIGHT")):
			# KEY RIGHT
			self.selection_mode = False
			if(self.curpos < len(self.text)): 
				self.curpos += 1
			else:
				beep()

	# handles Home/End
	def handle_home_end_keys(self, ch):
		if(KeyBindings.is_key(ch, "MOVE_CURSOR_TO_LINE_END")):
			# END
			self.selection_mode = False
			self.curpos = len(self.text)
		elif(KeyBindings.is_key(ch, "MOVE_CURSOR_TO_LINE_START")):
			# HOME
			self.selection_mode = False
			self.curpos = 0

	# handles Shift + Home/End
	def handle_shift_home_end_keys(self, ch):
		if(not self.selection_mode):
			self.selection_mode = True
			self.sel_start = self.curpos
		
		if(KeyBindings.is_key(ch, "SELECT_TILL_LINE_START")):
			# SHIFT+HOME
			self.curpos = 0
		elif(KeyBindings.is_key(ch, "SELECT_TILL_LINE_END")):
			# SHIFT+END
			self.curpos = len(self.text)
		
		self.sel_end = self.curpos

	# handles Shift + LeftArrow/RightArrow
	def handle_shift_arrow_keys(self, ch):
		if(not self.selection_mode):
			self.selection_mode = True
			self.sel_start = self.curpos

		if(KeyBindings.is_key(ch, "SELECT_CHARACTER_LEFT")):
			# SHIFT+LEFT
			if(self.curpos > 0): 
				self.curpos -= 1
			else:
				beep()
		if(KeyBindings.is_key(ch, "SELECT_CHARACTER_RIGHT")):
			# SHIFT+RIGHT
			if(self.curpos < len(self.text)): 
				self.curpos += 1
			else:
				beep()
		self.sel_end = self.curpos

	# selects all the text
	def handle_select_all(self):
		self.selection_mode = True
		self.sel_start = 0
		self.sel_end = len(self.text)

	def handle_cut(self):
		if(not self.selection_mode): return
		del_text = self.delete_selected_text()
		clipboard.copy(del_text)

	def handle_copy(self):
		if(not self.selection_mode): return
		offset, sel_text = self.get_selected_offset_and_text()
		clipboard.copy(sel_text)

	def handle_paste(self):
		data = clipboard.paste()
		if(self.selection_mode): self.delete_selected_text()
		self.text = self.text[0:self.curpos] + data + self.text[self.curpos:]
		self.curpos += len(data)

	# handles key presses
	def perform_action(self, ch):
		if(not self.is_in_focus): self.focus()
		if(ch == -1): return None
		
		if(KeyBindings.is_key(ch, "DELETE_CHARACTER_LEFT")):
			self.handle_backspace()
		elif(KeyBindings.is_key(ch, "DELETE_CHARACTER_RIGHT")):
			self.handle_delete()
		elif(KeyBindings.is_key(ch, "MOVE_CURSOR_TO_LINE_START") or KeyBindings.is_key(ch, "MOVE_CURSOR_TO_LINE_END")):
			self.handle_home_end_keys(ch)
		elif(KeyBindings.is_key(ch, "MOVE_CURSOR_LEFT") or KeyBindings.is_key(ch, "MOVE_CURSOR_RIGHT")):
			self.handle_arrow_keys(ch)
		elif(KeyBindings.is_key(ch, "SELECT_TILL_LINE_START") or KeyBindings.is_key(ch, "SELECT_TILL_LINE_END")):
			self.handle_shift_home_end_keys(ch)
		elif(KeyBindings.is_key(ch, "SELECT_CHARACTER_LEFT") or KeyBindings.is_key(ch, "SELECT_CHARACTER_RIGHT")):
			self.handle_shift_arrow_keys(ch)
		elif(KeyBindings.is_key(ch, "SELECT_ALL")):
			self.handle_select_all()
		elif(KeyBindings.is_key(ch, "COPY")):
			self.handle_copy()
		elif(KeyBindings.is_key(ch, "CUT")):
			self.handle_cut()
		elif(KeyBindings.is_key(ch, "PASTE")):
			self.handle_paste()
		else:
			char = str(chr(ch))
			if(self.charset.find(char) != -1):
				if(not self.numeric or self.numeric_charset.find(char) != -1):
					if(self.maxlen < 0 or self.curpos < self.maxlen-1):					
						self.text = (self.text[0:self.curpos] if self.curpos>0 else "") + char + (self.text[self.curpos:] if self.curpos<len(self.text) else "")
						self.curpos += 1
					else:						
						if(self.callback == None): return
				else:
					if(self.callback == None): return
			else:
				if(self.callback == None): return
		
		if(self.callback != None): self.callback(ch)
		self.repaint()

	# draws the textfield
	def repaint(self):
		curses.curs_set(self.is_in_focus)
		paint_theme = self.theme
		if(self.is_in_focus and self.focus_theme != None): paint_theme = self.focus_theme
		
		self.parent.addstr(self.y, self.x, " " * self.width, paint_theme)
		
		n = len(self.text)
		if(n <= self.width):
			self.parent.addstr(self.y, self.x, self.text, paint_theme)
			rendered_curpos = self.curpos
			self.start = 0
			self.end = min([self.width, n])
		else:
			n = len(self.text)
			if(self.curpos < self.start):
				self.start = self.curpos
				self.end = min([self.start + self.width, n])
			elif(self.curpos > self.end):
				self.end = min([n, self.curpos + 1])
				self.start = max([0, self.curpos - self.width + 1])
			
			vtext = self.text[self.start:self.end]
			vcurpos = self.curpos - self.start
			self.parent.addstr(self.y, self.x, vtext, paint_theme)
			rendered_curpos = vcurpos
		
		self.print_selected_text()
		self.parent.move(self.y, self.x + rendered_curpos)
		
	def print_selected_text(self):
		if(not self.selection_mode): return

		offset, sel_text = self.get_selected_offset_and_text()
		self.parent.addstr(self.y, self.x + offset, sel_text, gc("selection"))
	
	def get_selected_offset_and_text(self):
		if(not self.selection_mode): return (0, "")

		if(self.sel_start > self.sel_end):
			sel_start, sel_end = self.sel_end, self.sel_start
		else:
			sel_start, sel_end = self.sel_start, self.sel_end

		if(sel_end <= self.start or sel_start >= self.end or sel_start == sel_end): return (0, "")
		
		start = max([self.start, sel_start])
		end = min([self.end, sel_end])
		offset = start - self.start
		sel_text = self.text[start:end]

		return(offset, sel_text)

	# returns the text of the textfield
	def __str__(self):
		return self.text

	def on_click(self, y, x):
		intended_curpos = x - self.start
		if(intended_curpos > len(self.text)): intended_curpos = len(self.text)
		self.curpos = intended_curpos
		self.repaint()