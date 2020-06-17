from ash.widgets import *
from ash.widgets.utils.utils import *
from ash.widgets.utils.formatting import *

class Window:
	def __init__(self, y, x, height, width, title):
		self.y = y
		self.x = x
		self.height = height
		self.width = width
		self.widgets = []
		self.widget_map = dict()
		self.active_widget_index = -1
		self.title = (title if len(title) <= self.width-2 else title[0:self.width-2])
		
	def get_width(self):
		return self.width

	def get_height(self):
		return self.height

	def set_title(self, title):
		self.title = (title if len(title) <= self.width-2 else title[0:self.width-2])
		self.repaint()

	def repaint(self):
		pass

	def show(self):
		pass

	def hide(self):
		self.win = None

	def addstr(self, y, x, str, theme):
		if(self.win != None): self.win.addstr(y, x, str, theme)

	def move(self, newy, newx):
		if(self.win != None): self.win.move(newy, newx)

	def get_active_widget(self):
		if(self.active_widget_index < 0):
			return None
		else:
			return self.widgets[self.active_widget_index]

	def get_widget(self, widget_name):
		index = self.widget_map.get(widget_name)
		if(index == None): return None
		return self.widgets[index]

	def add_widget(self, widget_name, widget):
		self.widgets.append(widget)
		self.widget_map[widget_name] = len(self.widgets) - 1

		if(self.active_widget_index == -1): 
			self.active_widget_index = self.get_next_focussable_widget_index()
			if(self.active_widget_index > -1):
				self.widgets[self.active_widget_index].focus()
	
	# <---------------------- private functions -------------------->
	def get_previous_focussable_widget_index(self):
		count = len(self.widgets)
		if(count == 0): return -1

		if(self.active_widget_index == -1):
			start_index = count - 1
		else:
			start_index = (self.active_widget_index - 1) % count
		
		index = start_index

		while(True):
			if(self.widgets[index].is_focussable()):
				return index
			else:
				index = (index - 1) % count
				if(index == start_index): return -1

	def get_next_focussable_widget_index(self):
		count = len(self.widgets)
		if(count == 0): return -1

		start_index = (self.active_widget_index + 1) % count
		index = start_index

		while(True):
			if(self.widgets[index].is_focussable()):
				return index
			else:
				index = (index + 1) % count
				if(index == start_index): return -1