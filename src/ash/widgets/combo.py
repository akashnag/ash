from ash.widgets import *
from ash.widgets.listbox import *

class Combo(ListBox):
	def __init__(self, parent, y, x, width, items, theme, focus_theme):
		super(Combo, self).__init__(parent, y, x, width, 1, items, theme, focus_theme)