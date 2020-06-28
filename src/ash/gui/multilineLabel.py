# ---------------------------------------------------------------------------------------------
#  Copyright (c) Akash Nag. All rights reserved.
#  Licensed under the MIT License. See LICENSE.md in the project root for license information.
# ---------------------------------------------------------------------------------------------

# This module implements a multiline label widget

from ash.gui import *

class MultilineLabel(Widget):
	def __init__(self, parent, y, x, width, text, theme):
		super().__init__(WIDGET_TYPE_MULTILINE_LABEL, False)
		self.parent = parent
		self.y = y
		self.x = x
		self.width = width
		self.theme = theme
		self.text = text
		self.repaint()
	
	# draw the label using word-wrap wherever required
	def repaint(self):
		n = len(self.text)
		row = self.y
		text = self.text

		while(n > width):
			sub = text[0:width]
			if(sub.find("\n") == -1):
				if(text[width] != " "):
					pos = sub.rfind(" ")
					if(pos == -1):
						sub = text[0:width-1] + "-"
						text = "-" + text[width-1:]
					else:
						sub = text[0:pos]
						text = text[pos+1:]
				else:
					text = text[width:]
			else:
				pos = sub.find("\n")
				sub = sub[0:pos]
				text = text[pos+1:]

			self.parent.addstr(row, self.x, sub, self.theme)
			n = len(text)
			row += 1

		self.parent.addstr(row, self.x, text, self.theme)

	# returns the label text
	def __str__(self):
		return self.text