# ---------------------------------------------------------------------------------------------
#  Copyright (c) Akash Nag. All rights reserved.
#  Licensed under the MIT License. See LICENSE.md in the project root for license information.
# ---------------------------------------------------------------------------------------------

# This module implements the ModalDialog window

from ash.widgets import *
from ash.widgets.window import *
from ash.widgets.utils.utils import *

MSGBOX_OK		= 1
MSGBOX_CANCEL	= 2
MSGBOX_YES		= 3
MSGBOX_NO		= 4

class MessageBox(Window):
	def __init__(self, parent, y, x, height, width, title, message):
		super().__init__(y, x, height, width, title)
		self.parent = parent
		self.theme = gc(COLOR_MSGBOX)
		self.message = message
		self.win = None

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
			if(ch > -1): 
				response = self.check_response(ch)
				if(response > 0):
					self.win.clear()
					return self.check_response(ch)
				else:
					beep()
		
	# draw the window
	def repaint(self):
		if(self.win == None): return

		self.win.clear()
		self.win.attron(self.theme)
		self.win.border()
		
		for h in range(1, self.height-1):
			self.win.addstr(h, 1, " " * (self.width-2), self.theme)

		self.win.addstr(1, 2, self.title, curses.A_BOLD | self.theme)
		
		lines = self.message.splitlines()
		i = 2
		for line in lines:
			self.win.addstr(i, 2, line, self.theme)
			i += 1

		self.win.attroff(self.theme)		
		self.win.refresh()

	# check the response
	def check_response(self, ch):
		s = str(chr(ch))
		if(s == "y" or s == "Y"):
			return MSGBOX_YES
		elif(s == "n" or s == "N"):
			return MSGBOX_NO
		elif(s == "o" or s == "O" or is_newline(ch)):
			return MSGBOX_OK
		elif(s == "c" or s == "C"):
			return MSGBOX_CANCEL
		else:
			return -1