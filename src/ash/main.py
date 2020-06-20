# ---------------------------------------------------------------------------------------------
#  Copyright (c) Akash Nag. All rights reserved.
#  Licensed under the MIT License. See LICENSE.md in the project root for license information.
# ---------------------------------------------------------------------------------------------

from ash import *

APP_MODE_BLANK		= 1		# if ash is invoked without arguments
APP_MODE_FILE		= 2		# if ash is invoked with one or more file names
APP_MODE_PROJECT	= 3		# if ash is invoked with "-d" followed by a directory name

class AshEditorApp:
	def __init__(self, args):
		self.args = args
		
	def run(self):
		# TO DO: check arguments and set flags
		pass

		# invoke the GUI initialization routine
		curses.wrapper(self.app_main)

	# initialize the GUI
	def app_main(self, stdscr):
		init_colors()
		curses.raw()
		
		self.main_window = TopLevelWindow(stdscr, "Ash v1.0", self.key_handler)
		self.main_window.add_status_bar(StatusBar(self.main_window, [ 1.0 ]))		
		
		txtEditor = Editor(self.main_window, 1, 0, 2, 0)
		self.main_window.add_widget("txtEditor", txtEditor)
		self.main_window.show()
		
	# FOR TESTING: primary key handler to receive all key combinations
	def key_handler(self, ch):
		if(is_ctrl(ch, "Q")):
			self.main_window.hide()
		else:
			#x = str(self.main_window.get_widget("txtName"))
			self.main_window.get_status_bar().set(0, str(curses.keyname(ch)))
			#txtEditor = self.main_window.get_widget("txtEditor")
			#nlen = len(txtEditor.lines[txtEditor.curpos.y])
			#self.main_window.get_status_bar().set(0, str(txtEditor.selection_mode) + " -> " + str(txtEditor.sel_start) + " : " + str(txtEditor.sel_end))
			##self.main_window.win.addstr(1,1, str(self.main_window.get_widget("txtName")), gc())
		return ch