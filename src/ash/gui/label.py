# ---------------------------------------------------------------------------------------------
#  Copyright (c) Akash Nag. All rights reserved.
#  Licensed under the MIT License. See LICENSE.md in the project root for license information.
# ---------------------------------------------------------------------------------------------

# This module implements the Label widget

from ash.gui import *

class Label(Widget):
	def __init__(self, parent, y, x, text, theme):
		super().__init__(WIDGET_TYPE_LABEL, False)
		self.parent = parent
		self.y = y
		self.x = x
		self.theme = theme
		self.text = text
	
	# draw the label
	def repaint(self):
		self.parent.addstr(self.y, self.x, self.text, self.theme)

	# sets the text of the label
	def set_text(self, text):
		self.text = text

	# returns the text of the label
	def __str__(self):
		return self.text