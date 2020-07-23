# ---------------------------------------------------------------------------------------------
#  Copyright (c) Akash Nag. All rights reserved.
#  Licensed under the MIT License. See LICENSE.md in the project root for license information.
# ---------------------------------------------------------------------------------------------

# This module implements the ModalDialog window

from ash.gui import *
from ash.gui.window import *

class ModalDialog(Window):
	def __init__(self, parent, y, x, height, width, title, handler_func):
		super().__init__(y, x, height, width, title)
		self.parent = parent
		self.theme = gc("outer-border")
		self.handler_func = handler_func
		self.win = None

	# show the window and start the event-loop
	def show(self):
		self.win = curses.newwin(self.height, self.width, self.y, self.x)
		
		curses.curs_set(False)
		self.win.keypad(True)
		self.win.timeout(0)		
		self.repaint()

		while(self.win != None):
			ch = self.win.getch()
			if(ch == -1): continue
			
			if(self.handler_func != None):
				ch = self.handler_func(ch)
				if(self.win == None): return
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
			
			if(ch > -1):
				if(KeyBindings.is_mouse(ch)):
					btn, y, x = KeyBindings.get_mouse(ch)
					if(btn == MOUSE_CLICK):
						for i, w in enumerate(self.widgets):
							if(is_enclosed(y, x, w.get_bounds())):
								self.get_active_widget().blur()
								w.focus()
								self.active_widget_index = i
								ry, rx = w.get_relative_coords(y,x)
								w.on_click(ry,rx)
								break
					if(self.handler_func != None and is_enclosed(y, x, (self.y + 1, self.x + self.width - 3, 1, 1) )):
						self.handler_func(KeyBindings.get_key("CLOSE_WINDOW"))
				elif(self.active_widget_index > -1):
					self.get_active_widget().perform_action(ch)

			self.repaint()
		
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
		
		# active widget must be repainted last to correctly position cursor
		aw = self.get_active_widget()
		for w in self.widgets: 
			if(w != aw): w.repaint()

		if(aw != None): aw.repaint()
		self.win.refresh()