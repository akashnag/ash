# ---------------------------------------------------------------------------------------------
#  Copyright (c) Akash Nag. All rights reserved.
#  Licensed under the MIT License. See LICENSE.md in the project root for license information.
# ---------------------------------------------------------------------------------------------

# This module implements the MessageBox window

from ash.gui import *
from ash.gui.window import *
from ash.utils.keyUtils import *

MSGBOX_OK		= 1
MSGBOX_CANCEL	= 2
MSGBOX_YES		= 3
MSGBOX_NO		= 4

MSGBOX_TYPE_OK				= 0
MSGBOX_TYPE_OK_CANCEL		= 1
MSGBOX_TYPE_YES_NO			= 2
MSGBOX_TYPE_YES_NO_CANCEL	= 3

class MessageBox(Window):
	def __init__(self, parent, title, message, type = MSGBOX_TYPE_OK):
		msg_lines, msg_len = get_message_dimensions(message)
		msg_len = max([msg_len, len(title), len("Y(ES) | N(O) | (C)ANCEL")])
		y, x = get_center_coords(parent, msg_lines + 5, msg_len + 4)

		super().__init__(y, x, msg_lines + 5, msg_len + 4, title)
		self.type = type
		self.parent = parent.stdscr
		self.border_theme = gc("messagebox-border")
		self.theme = gc("messagebox-background")
		self.message = message
		self.title = title
		self.win = None

		if(self.type == MSGBOX_TYPE_OK):
			self.message += "\n" + "(O)K".center(self.width-3)
		elif(self.type == MSGBOX_TYPE_OK_CANCEL):
			self.message += "\n" + "(O)K | (C)ANCEL".center(self.width-3)
		elif(self.type == MSGBOX_TYPE_YES_NO):
			self.message += "\n" + "(Y)ES | (N)O".center(self.width-3)
		elif(self.type == MSGBOX_TYPE_YES_NO_CANCEL):
			self.message += "\n" + "(Y)ES | (N)O | (C)ANCEL".center(self.width-3)

	# show the window and start the event-loop
	def show(self):
		self.win = curses.newwin(self.height, self.width, self.y, self.x)
		
		curses.curs_set(False)
		self.win.keypad(True)
		self.win.timeout(0)		
		self.repaint()

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
		self.win.attron(self.border_theme)
		self.win.border()
		self.win.addstr(2, 0, BORDER_SPLIT_RIGHT, self.theme)
		self.win.addstr(2, self.width-1, BORDER_SPLIT_LEFT, self.theme)
		
		for h in range(1, self.height-1):
			self.win.addstr(h, 1, " " * (self.width-2), self.theme)

		self.win.addstr(2, 1, BORDER_HORIZONTAL * (self.width-2), self.theme)
		self.win.addstr(1, 2, self.title, curses.A_BOLD | self.theme)
		
		lines = self.message.splitlines()
		i = 3
		n = len(lines)
		for k in range(n):
			self.win.addstr(i, 2, lines[k], (self.theme if k < n-1 else curses.A_BOLD | self.theme))
			i += 1

		self.win.attroff(self.theme)		
		self.win.refresh()

	# check the response
	def check_response(self, ch):
		s = str(chr(ch)).lower()
		if(s == "y" and (self.type == MSGBOX_TYPE_YES_NO or self.type == MSGBOX_TYPE_YES_NO_CANCEL)):
			return MSGBOX_YES
		elif(s == "n" and (self.type == MSGBOX_TYPE_YES_NO or self.type == MSGBOX_TYPE_YES_NO_CANCEL)):
			return MSGBOX_NO
		elif((s == "o" or KeyBindings.is_key(ch, "SAVE_AND_CLOSE_WINDOW")) and (self.type == MSGBOX_TYPE_OK or self.type == MSGBOX_TYPE_OK_CANCEL)):
			return MSGBOX_OK
		elif(s == "c" and (self.type == MSGBOX_TYPE_YES_NO_CANCEL or self.type == MSGBOX_TYPE_OK_CANCEL)):
			return MSGBOX_CANCEL
		else:
			return -1