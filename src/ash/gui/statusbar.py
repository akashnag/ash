# ---------------------------------------------------------------------------------------------
#  Copyright (c) Akash Nag. All rights reserved.
#  Licensed under the MIT License. See LICENSE.md in the project root for license information.
# ---------------------------------------------------------------------------------------------

# This module implements the StatusBar widget

from ash.gui import *

class StatusBar(Widget):
	def __init__(self, parent, section_widths, supports_colors=True):
		super().__init__(WIDGET_TYPE_STATUSBAR, False, False)
		self.parent = parent
		self.section_widths = section_widths
		self.supports_colors = supports_colors
		self.sections = [ "" for i in range(len(section_widths)) ]
		self.alignments = [ "left" for i in range(len(section_widths)) ]

	# set status text for a given section
	def set(self, section_id, text, alignment = "left"):
		self.sections[section_id] = text
		self.alignments[section_id] = alignment

	# returns the status text of a given section
	def get(self, section_id):
		return self.sections[section_id]

	# returns the status text as a whole
	def __str__(self):
		str = ""
		# TO DO: subtraction of 1 should not be necessary
		# but curses.window.addstr() throws error as cursor has no place to go
		curses.curs_set(False)
		w = int(self.parent.get_width()) - 1
		cumw = 0
		for i in range(len(self.section_widths)):
			if(self.section_widths[i] <= 0):			# use all of the remaining space
				remw = w - cumw
				if(self.section_widths[i] == 0):		# 0 = align left
					str += (" " + self.sections[i] + " ").ljust(remw)
				elif(self.section_widths[i] == -1):		# negative = align right
					str += (" " + self.sections[i] + " ").rjust(remw)
			elif(self.section_widths[i] > 0 and self.section_widths[i] < 1):
				secw = round(self.section_widths[i] * w)
				str += (" " + self.sections[i] + " ").ljust(secw)
				cumw += secw
			elif(self.section_widths[i] >= 1):
				str += (" " + self.sections[i] + " ").ljust(self.section_widths[i])
				cumw += self.section_widths[i]

		if(len(str) > w):
			return str[0:w]
		else:
			return str + (" " * (w - len(str)))

	def repaint(self, win, width, y, x):				# called from TopLevelWindow
		n = len(self.sections)
		curses.curs_set(False)
		cumw = 0
		for i in range(n):
			w = self.section_widths[i]
			if(w == -1): 
				w = width - cumw
			elif(w > 0 and w < 1):
				w = round(width * w)

			s = " " + ("" if self.sections[i] == None else str(self.sections[i])) + " "

			if(self.alignments[i] == "left"):
				s = s.ljust(w)
			elif(self.alignments[i] == "center"):
				s = s.center(w)
			elif(self.alignments[i] == "right"):
				s = s.rjust(w)

			if(cumw + w > width): 
				s = s[0:width-cumw]
				win.addstr(y, x + cumw, s, gc("status-" + str(i)) | (0 if self.supports_colors else curses.A_REVERSE))
				return
				
			try:
				win.addstr(y, x + cumw, s, gc("status-" + str(i)) | (0 if self.supports_colors else curses.A_REVERSE))
			except:
				pass
			cumw += w