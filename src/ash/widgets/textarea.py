from ash.widgets import *
from ash.widgets.utils.utils import *
from ash.widgets.utils.formatting import *

class TextArea(Widget):
	def __init__(self, parent, y, x, height, width, theme, focus_theme = None, maxlen = -1):
		super().__init__(WIDGET_TYPE_TEXTAREA)
		self.y = y
		self.x = x
		self.height = height
		self.width = width
		self.curpos = 0
		self.theme = theme
		self.text = ""
		self.parent = parent
		self.maxlen = maxlen
		self.focus_theme = focus_theme
		self.is_in_focus = False

		self.charset = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789"
		self.charset += "~`!@#$%^&*()-_=+\\|[{]};:\'\",<.>/? \n"
		
		self.focus()
	
	def focus(self):
		self.is_in_focus = True
		self.repaint()

	def blur(self):
		self.is_in_focus = False
		self.repaint()

	def perform_action(self, ch):
		self.focus()

		if(ch == -1):
			self.repaint()
			return None
		
		if(ch == curses.KEY_BACKSPACE):
			if(self.curpos > 0):
				self.text = (self.text[0:self.curpos-1] if self.curpos > 1 else "") + (self.text[self.curpos:] if self.curpos < len(self.text) else "")
				self.curpos -= 1
			else:
				curses.beep()
		elif(ch == curses.KEY_DC):
			if(self.curpos == len(self.text)):
				curses.beep()
			else:
				self.text = (self.text[0:self.curpos] if self.curpos > 0 else "") + (self.text[self.curpos+1:] if self.curpos < len(self.text)-1 else "")
		elif(ch == curses.KEY_END):
			self.curpos = len(self.text)
		elif(ch == curses.KEY_HOME):
			self.curpos = 0
		elif(ch == curses.KEY_LEFT):
			if(self.curpos > 0): 
				self.curpos -= 1
			else:
				curses.beep()
		elif(ch == curses.KEY_RIGHT):
			if(self.curpos < len(self.text)): 
				self.curpos += 1
			else:
				curses.beep()
		else:
			char = str(chr(ch))
			if(self.charset.find(char) != -1):
				if(self.maxlen < 0 or self.curpos < self.maxlen-1):					
					self.text = (self.text[0:self.curpos] if self.curpos>0 else "") + char + (self.text[self.curpos:] if self.curpos<len(self.text) else "")
					self.curpos += 1
				else:
					curses.beep()				
			else:
				curses.beep()
		
		self.repaint()

	def repaint(self):
		if(self.is_in_focus): curses.curs_set(True)
		paint_theme = self.theme
		if(self.is_in_focus and self.focus_theme != None): paint_theme = self.focus_theme
		
		for h in range(self.height):
			self.parent.addstr(self.y + h, self.x, " " * self.width, paint_theme)
		
		self.lines, (self.curpos_row, self.curpos_col) = self.__get_lines()
		nlines = len(self.lines)

		if(nlines <= self.height):
			for i in range(nlines):
				self.parent.addstr(self.y + i, self.x, self.lines[i], paint_theme)
			self.parent.move(self.y + self.curpos_row, self.x + self.curpos_col)
		else:
			flank = self.height // 2
			start = self.curpos_row - flank
			end = self.curpos_row + flank

			if(start < 0):
				delta = abs(start)
				start += delta
				end += delta				
			elif(end > nlines):
				delta = end - nlines
				start -= delta
				end -= delta
			
			vcurpos_row = self.curpos_row - start
			for i in range(start, end):
				self.parent.addstr(self.y + i - start, self.x, self.lines[i], paint_theme)
			self.parent.move(self.y + vcurpos_row, self.x + self.curpos_col)
		
	def __str__(self):
		return self.text

	def __get_lines(self):
		lines = list()
		
		c = self.curpos
		cumadd = 0
		n = len(self.text)
		row = 0
		text = self.text
		width = self.width

		while(n > width):
			sub = text[0:width]

			offset = 0
			if(sub.find("\n") == -1):
				if(text[width] != " "):
					pos = sub.rfind(" ")
					if(pos == -1):
						sub = text[0:width-1] + "-"
						text = "-" + text[width-1:]
					else:
						sub = text[0:pos+1]
						text = text[pos+1:]
				else:
					text = text[width:]
			else:
				pos = sub.find("\n")
				sub = sub[0:pos]
				text = text[pos+1:]
				offset = 1

			if(c >= cumadd and c <= cumadd + offset + len(sub)):
				cpos = ( row, c - cumadd)

			lines.append(sub)
			cumadd += len(sub) + offset
			n = len(text)
			row += 1
		
		while(text.find("\n") > -1):
			pos = text.find("\n")
			sub = text[0:pos]
			text = text[pos+1:]
			offset = 1

			if(c >= cumadd and c <= cumadd + offset + len(sub)):
				cpos = ( row, c - cumadd)

			lines.append(sub)
			cumadd += len(sub) + offset
			row += 1

		lines.append(text)
		if(c >= cumadd and c <= cumadd + len(text)):
			cpos = ( row, c - cumadd)
		elif( c > cumadd + len(text)):
			cpos = ( row, c - cumadd + 1)

		return ( lines, cpos )