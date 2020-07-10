# ---------------------------------------------------------------------------------------------
#  Copyright (c) Akash Nag. All rights reserved.
#  Licensed under the MIT License. See LICENSE.md in the project root for license information.
# ---------------------------------------------------------------------------------------------

# This module implements the InputBox window

from ash.gui import *
from ash.gui.window import *
from ash.gui.textfield import *

class InputBox(Window):
	def __init__(self, parent, title, prompt, default = ""):
		msg_lines, msg_len = get_message_dimensions(prompt)
		msg_len = max([msg_len, len(title), len("Y(ES) | N(O) | (C)ANCEL")])
		y, x = get_center_coords(parent, msg_lines + 5, msg_len + 4)

		super().__init__(y, x, msg_lines + 5, msg_len + 4, title)
		self.type = type
		self.parent = parent.stdscr
		self.border_theme = gc("outer-border")
		self.theme = gc("outer-border")
		self.prompt = prompt
		self.title = title
		self.default = default
		self.win = curses.newwin(self.height, self.width, self.y, self.x)
		self.add_widget("txtInput", TextField(self, self.height-2, 2, self.width-4, self.default))
		

	# show the window and start the event-loop
	def show(self):
		#self.win = curses.newwin(self.height, self.width, self.y, self.x)
		
		curses.curs_set(False)
		self.win.keypad(True)
		self.win.timeout(0)		
		self.repaint()

		# start of the event loop	
		while(True):
			ch = self.win.getch()
			if(ch > -1): 
				response = self.check_response(ch)
				if(response == 0):
					self.win.clear()
					return ""
				elif(response != None):
					self.win.clear()
					return response				
		
	# draw the window
	def repaint(self):
		if(self.win == None): return

		self.win.clear()
		self.win.attron(self.border_theme)
		self.win.border()
		self.win.addstr(2, 0, BORDER_SPLIT_RIGHT, self.theme)
		self.win.addstr(2, self.width-1, BORDER_SPLIT_LEFT, self.theme)
		
		for h in range(1, self.height-1):
			self.win.addstr(h, 1, " " * (self.width-2), self.theme)

		self.win.addstr(2, 1, BORDER_HORIZONTAL * (self.width-2), self.theme)
		self.win.addstr(1, 2, self.title, curses.A_BOLD | self.theme)
		
		lines = self.prompt.splitlines()
		i = 3
		n = len(lines)
		for k in range(n):
			self.win.addstr(i, 2, lines[k], (self.theme if k < n-1 else curses.A_BOLD | self.theme))
			i += 1

		self.win.attroff(self.theme)
		for w in self.widgets:
			w.repaint()
		self.win.refresh()

	# check the response
	def check_response(self, ch):
		if(is_newline(ch)):
			return str(self.get_widget("txtInput"))
		elif(is_ctrl(ch, "Q")):
			return 0
		else:
			self.get_widget("txtInput").perform_action(ch)
			return None