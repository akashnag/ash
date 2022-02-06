# ---------------------------------------------------------------------------------------------
#  Copyright (c) Akash Nag. All rights reserved.
#  Licensed under the MIT License. See LICENSE.md in the project root for license information.
# ---------------------------------------------------------------------------------------------

# This module implements the CheckBox widget

from ash.gui import *

class CheckBox(Widget):
	def __init__(self, parent, y, x, text):
		super().__init__(WIDGET_TYPE_CHECKBOX)
		self.parent = parent
		self.y = y
		self.x = x
		self.height = 1
		self.width = len(text) + 3
		self.theme = gc("formfield")
		self.focus_theme = gc("formfield-focussed")
		self.text = text
		self.is_in_focus = False
		self.checked = False
		self.repaint()

	# when checkbox receives focus
	def focus(self):
		self.is_in_focus = True
		self.repaint()

	# when checkbox loses focus
	def blur(self):
		self.is_in_focus = False
		self.repaint()

	# returns checkbox state
	def is_checked(self):
		return self.checked

	# draws the checkbox
	def repaint(self):
		if(self.is_in_focus): curses.curs_set(False)

		paint_theme = self.theme
		if(self.is_in_focus and self.focus_theme != None): paint_theme = self.focus_theme

		if(self.checked):
			s = CHECKED_BOX + "  " + self.text + " "
		else:
			s = UNCHECKED_BOX + "  " + self.text + " "
		
		self.parent.addstr(self.y, self.x, s, paint_theme)
	
	# when keypress occurs: space toggles checkbox state
	def perform_action(self, ch):
		self.focus()
		if(KeyBindings.is_key(ch, "CHANGE_VALUE")):
			self.checked = not self.checked
			self.repaint()
		else:
			beep()

	# returns the string representation: checkbox text
	def __str__(self):
		return self.text

	# set the checked-status of the checkbox
	def set_value(self, checked = True):
		self.checked = checked

	def on_click(self, y, x):
		self.checked = not self.checked
		self.repaint()