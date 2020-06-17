from ash.widgets import *

class Label(Widget):
	def __init__(self, parent, y, x, text, theme):
		super().__init__(WIDGET_TYPE_LABEL, False)
		self.parent = parent
		self.y = y
		self.x = x
		self.theme = theme
		self.text = text
	
	def repaint(self):
		self.parent.addstr(self.y, self.x, self.text, self.theme)

	def set_text(self, text):
		self.text = text

	def __str__(self):
		return self.text