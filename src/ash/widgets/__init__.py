# ---------------------------------------------------------------------------------------------
#  Copyright (c) Akash Nag. All rights reserved.
#  Licensed under the MIT License. See LICENSE.md in the project root for license information.
# ---------------------------------------------------------------------------------------------

import curses

from ash.widgets.utils.formatting import *
from ash.widgets.utils.utils import *
from ash.widgets.utils.colors import *
from ash.widgets.utils.dataUtils import *
from ash.widgets.utils.fileData import *
from ash.widgets.utils.editHistory import *

clipboard = None

import copy
import sys
import os
import pathlib
import select

# Check if xsel/pyperclip is present, then use it, else use internal-clipboard
try:
	import pyperclip as clipboard
	clipboard.paste()
except:
	from ash.widgets.utils.internalClipboard import InternalClipboard as clipboard


# define the widget type constants
WIDGET_TYPE_LABEL			= 1
WIDGET_TYPE_MULTILINE_LABEL	= 2
WIDGET_TYPE_TEXTFIELD 		= 3
WIDGET_TYPE_PASSWORD 		= 4
WIDGET_TYPE_TEXTAREA 		= 5
WIDGET_TYPE_CHECKBOX 		= 6
WIDGET_TYPE_LISTBOX 		= 7
WIDGET_TYPE_EDITOR			= 8
WIDGET_TYPE_STATUSBAR		= 9

# This is the abstract Widget class from which all widgets are derived
class Widget:
	def __init__(self, type, focussable = True, handles_tab = False):
		self.type = type
		self.focussable = focussable
		self.handles_tab = handles_tab
		self.is_in_focus = False

	def does_handle_tab(self):
		return self.handles_tab

	def is_focussable(self):
		return self.focussable

	def get_type(self):
		return self.type

	def focus(self):
		self.is_in_focus = True

	def blur(self):
		self.is_in_focus = False

	def perform_action(self, ch):
		pass

	def repaint(self):
		pass

	def readjust(self):
		pass