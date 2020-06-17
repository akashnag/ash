# ---------------------------------------------------------------------------------------------
#  Copyright (c) Akash Nag. All rights reserved.
#  Licensed under the MIT License. See LICENSE.md in the project root for license information.
# ---------------------------------------------------------------------------------------------

# This module implements the Combo-box widget by setting the
# height of a ListBox to 1 by default, and increasing it when
# state is toggled to dropdown.

from ash.widgets import *
from ash.widgets.listbox import *

class Combo(ListBox):
	def __init__(self, parent, y, x, width, items, theme, focus_theme):
		super(Combo, self).__init__(parent, y, x, width, 1, items, theme, focus_theme)
		self.drop_down = False

	# draws the combobox
	def repaint(self):
		if(self.drop_down):
			# add code: to show the dropdown list
			pass
		else:
			super().repaint()

	# Handle arrow keys like listbox, but toggle dropdown
	# list display on Space-key
	def perform_action(self, ch):
		if(ch == ord(" ")):
			self.drop_down = not self.drop_down
		else:
			super().perform_action(ch)