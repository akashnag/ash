# ---------------------------------------------------------------------------------------------
#  Copyright (c) Akash Nag. All rights reserved.
#  Licensed under the MIT License. See LICENSE.md in the project root for license information.
# ---------------------------------------------------------------------------------------------

# This module implements the Find & Replace dialog for entire project

from ash.gui import *
from ash.gui.window import *
from ash.gui.groupedListbox import *
from ash.gui.textfield import *
from ash.gui.checkbox import *

class ProjectFindReplaceDialog(Window):
	def __init__(self, parent, y, x, buffers, replace = False):
		super().__init__(y, x, 20, 70, ("SEARCH AND REPLACE IN ALL FILES" if replace else "SEARCH IN ALL FILES"))
		self.buffers = buffers
		self.parent = parent
		self.theme = gc("outer-border")
		self.win = None
		self.replace = replace
		self.mouse_drag_start = False
		
		self.txtFind = TextField(self, 4, 2, 66)
		if(self.replace): self.txtReplace = TextField(self, 6, 2, 66)
		
		self.chkMatchCase = CheckBox(self, (7 if self.replace else 5), 2, "Match case")
		self.chkWholeWords = CheckBox(self, (7 if self.replace else 5), 18, "Whole words")
		self.chkRegex = CheckBox(self, (7 if self.replace else 5), 35, "Regex")
		self.lstResults = GroupedListBox(self, (8 if self.replace else 6), 2, 66, (11 if self.replace else 13), "No results", supports_colors=self.parent.app.supports_colors)
		
		self.add_widget("txtFind", self.txtFind)
		if(self.replace): self.add_widget("txtReplace", self.txtReplace)
		self.add_widget("chkMatchCase", self.chkMatchCase)
		self.add_widget("chkWholeWords", self.chkWholeWords)
		self.add_widget("chkRegex", self.chkRegex)
		self.add_widget("lstResults", self.lstResults)

	# show the window and start the event-loop
	def show(self):
		self.win = curses.newwin(self.height, self.width, self.y, self.x)
		
		curses.curs_set(False)
		self.win.keypad(True)
		self.win.timeout(0)
		
		self.repaint()

		# start of the event loop	
		while(self.win != None):
			ch = self.win.getch()
			if(ch == -1): continue
			
			if(self.active_widget_index < 0 or not self.get_active_widget().does_handle_tab()):
				if(KeyBindings.is_key(ch, "FOCUS_NEXT") or KeyBindings.is_key(ch, "FOCUS_PREVIOUS")):
					old_index = self.active_widget_index
					if(KeyBindings.is_key(ch, "FOCUS_NEXT")):
						self.active_widget_index = self.get_next_focussable_widget_index()
					elif(KeyBindings.is_key(ch, "FOCUS_PREVIOUS")):
						self.active_widget_index = self.get_previous_focussable_widget_index()
					
					if(old_index != self.active_widget_index):
						if(old_index > -1): self.widgets[old_index].blur()
						if(self.active_widget_index > -1): self.widgets[self.active_widget_index].focus()

					ch = -1
				elif(is_window_movement_command(ch)):
					if(KeyBindings.is_key(ch, "MOVE_WINDOW_UP")):
						if(self.y > 1): self.y -= 1
					elif(KeyBindings.is_key(ch, "MOVE_WINDOW_DOWN")):
						if(self.y < self.parent.get_height() - self.get_height() - 1): self.y += 1
					elif(KeyBindings.is_key(ch, "MOVE_WINDOW_LEFT")):
						if(self.x > 0): self.x -= 1
					elif(KeyBindings.is_key(ch, "MOVE_WINDOW_RIGHT")):
						if(self.x < self.parent.get_width() - self.get_width()): self.x += 1
					
					self.win.mvwin(self.y, self.x)
					self.parent.repaint()
					ch = -1
			
			if(ch == -1): continue

			aw = None
			search_text = str(self.txtFind)
			if(self.replace): replace_text = str(self.txtReplace)

			if(KeyBindings.is_key(ch, "CLOSE_WINDOW")):
				self.hide()
				self.parent.repaint()
				return
			elif(self.replace and KeyBindings.is_key(ch, "REPLACE_ALL")):
				self.handle_replace_all(search_text, replace_text)
			elif(ch > -1):
				if(KeyBindings.is_mouse(ch)):
					btn, y, x = KeyBindings.get_mouse(ch)
					if(btn == MOUSE_CLICK):
						widget_found = False
						for i, w in enumerate(self.widgets):
							if(is_enclosed(y, x, w.get_bounds())):
								self.get_active_widget().blur()
								w.focus()
								self.active_widget_index = i
								ry, rx = w.get_relative_coords(y,x)
								w.on_click(ry,rx)
								aw = w
								widget_found = True
								break

						if((not widget_found) and is_enclosed(y, x, (self.y + 1, self.x + self.width - 3, 1, 1) )):
							self.hide()
							self.parent.repaint()
							return
					elif(btn == MOUSE_DOWN and is_enclosed(y, x, (self.y + 1, self.x + 1, 1, self.width - 2) )):
						self.mouse_drag_start = True
						self.mouse_drag_offset = (y, x)
					elif(btn == MOUSE_UP and self.mouse_drag_start):
						self.mouse_drag_start = False
						self.drag_window(y, x, *self.mouse_drag_offset)

				elif(self.active_widget_index > -1):
					aw =self.get_active_widget()
					aw.perform_action(ch)
				
				if(self.replace and aw != self.txtReplace and aw != self.lstResults):
					self.handle_find_all(str(self.txtFind))
				elif(aw != self.lstResults):
					self.handle_find_all(str(self.txtFind))				
					
			self.parent.repaint()
			self.repaint()
			self.parent.win.refresh()

			if(aw != None): aw.repaint()
	
	# drag the window
	def drag_window(self, y2, x2, y1, x1):
		delta_x = x2 - x1
		delta_y = y2 - y1

		new_y = self.y + delta_y
		new_x = self.x + delta_x

		max_y = self.parent.get_height() - self.get_height() - 1
		max_x = self.parent.get_width() - self.get_width()

		if(new_y < 1): new_y = 1
		if(new_x < 0): new_x = 0
		if(new_y > max_y): new_y = max_y
		if(new_x > max_x): new_x = max_x

		self.y = new_y
		self.x = new_x
		
		self.win.mvwin(self.y, self.x)
		self.parent.repaint()

	def handle_find_all(self, search_text):
		if(len(search_text.strip()) == 0):
			search_results = None
		else:
			search_results = self.buffers.find_all(search_text, self.chkMatchCase.is_checked(), self.chkWholeWords.is_checked(), self.chkRegex.is_checked())
		self.lstResults.display(search_results, self.parent.app.buffers)
		
	def handle_replace_all(self, search_text, replace_text):
		c, fc = self.buffers.replace_all(search_text, replace_text, self.chkMatchCase.is_checked(), self.chkWholeWords.is_checked(), self.chkRegex.is_checked())
		self.parent.app.show_error(f"{c} occurrences were replaced in {fc} buffers", False)

	def handle_fileopen(self, filename, curpos):			# called from groupedlistbox
		highlight_info = {
			"search_text": str(self.txtFind),
			"match_case": self.chkMatchCase.is_checked(),
			"whole_words": self.chkWholeWords.is_checked(),
			"is_regex": self.chkRegex.is_checked()
		}
		self.parent.open_in_new_tab(filename, curpos, highlight_info)
		self.hide()
		self.parent.repaint()

	# draw the window
	def repaint(self):
		if(self.win == None): return

		self.win.clear()
		self.win.attron(self.theme)
		self.win.border()
		self.win.attroff(self.theme)
		
		self.win.addstr(2, 0, BORDER_SPLIT_RIGHT, self.theme)
		self.win.addstr(2, self.width-1, BORDER_SPLIT_LEFT, self.theme)
		self.win.addstr(2, 1, BORDER_HORIZONTAL * (self.width-2), self.theme)

		self.win.addstr(1, 2, self.title, curses.A_BOLD | self.theme)
		self.win.addstr(1, self.width-3, "\u2a2f", curses.A_BOLD | self.theme)

		self.win.addstr(3, 2, "Find:", self.theme)
		if(self.replace): self.win.addstr(5, 2, "Replace with:", self.theme)
		
		# active widget must be repainted last, to correctly position cursor
		aw = self.get_active_widget()
		for w in self.widgets: 
			if(w != aw): w.repaint()

		if(aw != None): aw.repaint()
		self.win.refresh()