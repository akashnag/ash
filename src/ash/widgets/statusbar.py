from ash.widgets import *
from ash.widgets.utils.utils import *
from ash.widgets.utils.formatting import *

class StatusBar(Widget):
	def __init__(self, parent, section_widths):
		super().__init__(WIDGET_TYPE_STATUSBAR, False, False)
		self.parent = parent
		self.section_widths = section_widths
		self.sections = [ "" for i in range(len(section_widths)) ]

	def set(self, section_id, text):
		self.sections[section_id] = text

	def get(self, section_id):
		return self.sections[section_id]

	def __str__(self):
		str = ""
		# fix (in future) the following: subtraction of 1 should not be necessary
		w = int(self.parent.get_width())-1
		for i in range(len(self.section_widths)):
			width = int(w * float(self.section_widths[i]))
			str += pad_right_str(self.sections[i], width)
		return str