# ---------------------------------------------------------------------------------------------
#  Copyright (c) Akash Nag. All rights reserved.
#  Licensed under the MIT License. See LICENSE.md in the project root for license information.
# ---------------------------------------------------------------------------------------------

# This module implements the StatusBar widget

from ash.widgets import *
from ash.widgets.utils.utils import *
from ash.widgets.utils.formatting import *

class StatusBar(Widget):
	def __init__(self, parent, section_widths):
		super().__init__(WIDGET_TYPE_STATUSBAR, False, False)
		self.parent = parent
		self.section_widths = section_widths
		self.sections = [ "" for i in range(len(section_widths)) ]

	# set status text for a given section
	def set(self, section_id, text):
		self.sections[section_id] = text

	# returns the status text of a given section
	def get(self, section_id):
		return self.sections[section_id]

	# returns the status text as a whole
	def __str__(self):
		str = ""
		# TO DO: fix (in future) the following: 
		# subtraction of 1 should not be necessary
		# but curses.window.addstr() throws error as cursor has
		# no place to go
		w = int(self.parent.get_width()) - 1
		cumw = 0
		for i in range(len(self.section_widths)):
			if(self.section_widths[i] <= 0):			# use all of the remaining space
				remw = w - cumw
				if(self.section_widths[i] == 0):		# 0 = align left
					str += (" " + self.sections[i] + " ").ljust(remw)
				else:									# negative = align right
					str += (" " + self.sections[i] + " ").rjust(remw)
			else:
				str += (" " + self.sections[i] + " ").ljust(self.section_widths[i])
				cumw += self.section_widths[i]

		if(len(str) > w):
			return str[0:w]
		else:
			return str + (" " * (w - len(str)))