# ---------------------------------------------------------------------------------------------
#  Copyright (c) Akash Nag. All rights reserved.
#  Licensed under the MIT License. See LICENSE.md in the project root for license information.
# ---------------------------------------------------------------------------------------------

# This module implements a file load progress window

from ash import *
from ash.gui import *
from ash.gui.window import *

LOAD_STEP		= 1024			# bytes to read in each step

class FileLoader(Window):
	def __init__(self, parent, filename, encoding):
		y, x = get_center_coords(parent, 7, 50)
		super().__init__(y, x, 7, 50, "LOADING FILE")
		self.type = type
		self.parent = parent.stdscr
		self.border_theme = gc("outer-border")
		self.theme = gc("outer-border")
		self.win = curses.newwin(self.height, self.width, self.y, self.x)
		self.filename = filename
		self.encoding = encoding
		self.bytes_read = 0
		self.total_size = 0
		
	# show the window and start the event-loop
	def load(self):
		curses.curs_set(False)
		self.win.keypad(True)
		self.win.timeout(0)		
		self.repaint()

		activeFile = codecs.open(self.filename, "r", self.encoding)
		self.total_size = int(os.stat(self.filename).st_size)
		self.bytes_read = 0
		lines = list()

		while(True):
			ch = self.win.getch()			
			
			if(ch > -1 and KeyBindings.is_key(ch, "CANCEL_OPERATION")):
				activeFile.close()
				return None
			else:
				read_data = activeFile.readline()
				if(len(read_data) == 0): break
				self.bytes_read += len(read_data)
				lines.append(read_data[:-1])
				self.repaint(True)
		
		activeFile.close()
		self.win.clear()
		return lines
		
	# draw the window
	def repaint(self, partial=False):
		if(self.win == None): return

		if(not partial):
			self.win.clear()
			self.win.attron(self.border_theme)
			self.win.border()
			self.win.addstr(2, 0, BORDER_SPLIT_RIGHT, self.theme)
			self.win.addstr(2, self.width-1, BORDER_SPLIT_LEFT, self.theme)
			
			for h in range(1, self.height-1):
				self.win.addstr(h, 1, " " * (self.width-2), self.theme)

			self.win.addstr(2, 1, BORDER_HORIZONTAL * (self.width-2), self.theme)
			self.win.addstr(1, 2, self.title, curses.A_BOLD | self.theme)

			fn = get_file_title(self.filename)
			self.win.addstr(3, 2, (fn if len(fn) <= 46 else fn[0:46]), self.theme)

		if(self.total_size > 0):
			w = int((self.bytes_read / self.total_size) * (self.width - 4))
			self.win.addstr(5, 2, ("\u2588" * w).ljust(self.width-4), self.theme)
			self.win.refresh()

	# check the response
	def check_response(self, ch):
		if(KeyBindings.is_key(ch, "SAVE_AND_CLOSE_WINDOW")):
			return str(self.get_widget("txtInput"))
		elif(KeyBindings.is_key(ch, "CLOSE_WINDOW")):
			return 0
		else:
			self.get_widget("txtInput").perform_action(ch)
			return None