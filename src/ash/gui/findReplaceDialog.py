# ---------------------------------------------------------------------------------------------
#  Copyright (c) Akash Nag. All rights reserved.
#  Licensed under the MIT License. See LICENSE.md in the project root for license information.
# ---------------------------------------------------------------------------------------------

# This module implements the ModalDialog window

from ash.gui import *
from ash.gui.window import *
from ash.gui.textfield import *
from ash.core.utils import *
from ash.formatting.colors import *

class FindReplaceDialog(Window):
	def __init__(self, parent, y, x, ed, replace = False):
		super().__init__(y, x, (7 if replace else 5), 30, ("FIND AND REPLACE" if replace else "FIND"))
		self.ed = ed
		self.parent = parent
		self.theme = gc("outer-border")
		self.win = None
		self.ed.find_mode = True
		
		init_text = ""
		if(ed.selection_mode): init_text = ed.get_selected_text().replace("\n", "")
				
		self.txtFind = TextField(self, 3, 2, 26, init_text)
		self.txtReplace = TextField(self, 5, 2, 26)

		self.add_widget("txtFind", self.txtFind)
		if(replace): self.add_widget("txtReplace", self.txtReplace)

	# show the window and start the event-loop
	def show(self):
		self.win = curses.newwin(self.height, self.width, self.y, self.x)
		
		curses.curs_set(False)
		self.win.keypad(True)
		self.win.timeout(0)
		
		self.repaint()

		# start of the event loop	
		while(True):
			ch = self.win.getch()
			if(ch == -1): continue
			
			if(self.active_widget_index < 0 or not self.get_active_widget().does_handle_tab()):
				if((is_tab(ch) or ch == curses.KEY_BTAB)):
					old_index = self.active_widget_index
					if(is_tab(ch)):
						self.active_widget_index = self.get_next_focussable_widget_index()
					elif(ch == curses.KEY_BTAB):
						self.active_widget_index = self.get_previous_focussable_widget_index()
					
					if(old_index != self.active_widget_index):
						if(old_index > -1): self.widgets[old_index].blur()
						if(self.active_widget_index > -1): self.widgets[self.active_widget_index].focus()

					ch = -1
				elif(is_ctrl_arrow(ch)):
					if(is_ctrl_arrow(ch, "UP")):
						if(self.y > 1): self.y -= 1
					elif(is_ctrl_arrow(ch, "DOWN")):
						if(self.y < self.parent.get_height() - self.get_height() - 1): self.y += 1
					elif(is_ctrl_arrow(ch, "LEFT")):
						if(self.x > 0): self.x -= 1
					elif(is_ctrl_arrow(ch, "RIGHT")):
						if(self.x < self.parent.get_width() - self.get_width()): self.x += 1
					
					self.win.mvwin(self.y, self.x)
					self.parent.repaint()
					ch = -1
			
			if(ch == -1): continue

			search_text = str(self.get_widget("txtFind"))
			replace_text = str(self.get_widget("txtReplace"))

			if(is_ctrl(ch, "Q")):
				self.ed.cancel_find()
				self.hide()
				self.parent.repaint()
				self.ed.focus()
				return
			elif(is_newline(ch)):						# Enter: next
				self.handle_find_next_match(search_text)
			elif(is_func(ch, 7)):						# F7: previous
				self.handle_find_previous_match(search_text)
			elif(is_func(ch, 8)):						# F8: replace
				self.handle_replace(search_text, replace_text)
			elif(is_func(ch, 32)):						# Ctrl+F8: replace all
				self.handle_replace_all(search_text, replace_text)
			elif(self.active_widget_index > -1):
				self.get_active_widget().perform_action(ch)
				self.ed.find_all(str(self.txtFind))
				
			self.repaint()
			self.parent.win.refresh()
		
	def handle_find_next_match(self, search_text):
		self.ed.find_next(search_text)

	def handle_find_previous_match(self, search_text):
		self.ed.find_previous(search_text)

	def handle_replace(self, search_text, replace_text):
		self.ed.replace_next(search_text, replace_text)

	def handle_replace_all(self, search_text, replace_text):
		self.ed.replace_all(search_text, replace_text)

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
		
		# active widget must be repainted last to correctly position cursor
		aw = self.get_active_widget()
		for w in self.widgets: 
			if(w != aw): w.repaint()

		if(aw != None): aw.repaint()
		self.win.refresh()