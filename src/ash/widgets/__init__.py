import curses
from ash.widgets.utils.formatting import *
from ash.widgets.utils.utils import *

WIDGET_TYPE_LABEL			= 1
WIDGET_TYPE_MULTILINE_LABEL	= 2
WIDGET_TYPE_TEXTFIELD 		= 3
WIDGET_TYPE_PASSWORD 		= 4
WIDGET_TYPE_TEXTAREA 		= 5
WIDGET_TYPE_CHECKBOX 		= 6
WIDGET_TYPE_LISTBOX 		= 7
WIDGET_TYPE_EDITOR			= 8
WIDGET_TYPE_STATUSBAR		= 9

class Widget:
	def __init__(self, type, focussable = True, handles_tab = False):
		self.type = type
		self.focussable = focussable
		self.handles_tab = handles_tab

	def does_handle_tab(self):
		return self.handles_tab

	def is_focussable(self):
		return self.focussable

	def get_type(self):
		return self.type

	def focus(self):
		pass

	def blur(self):
		pass

	def perform_action(self, ch):
		pass

	def repaint(self):
		pass