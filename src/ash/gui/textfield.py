# ---------------------------------------------------------------------------------------------
#  Copyright (c) Akash Nag. All rights reserved.
#  Licensed under the MIT License. See LICENSE.md in the project root for license information.
# ---------------------------------------------------------------------------------------------

# This module implements the TextField widget

from ash.gui import *

class TextField(Widget):
	def __init__(self, parent, y, x, width, initial_text = "", numeric = False, maxlen = -1):
		super(TextField, self).__init__(WIDGET_TYPE_TEXTFIELD)
		self.y = y
		self.x = x
		self.width = width
		self.theme = gc("formfield")
		self.text = initial_text
		self.curpos = len(self.text)
		self.parent = parent
		self.numeric = numeric
		self.maxlen = maxlen
		self.focus_theme = gc("formfield-focussed")
		self.is_in_focus = False

		self.charset = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789"
		self.charset += "~`!@#$%^&*()-_=+\\|[{]};:\'\",<.>/? "			
		self.numeric_charset = "-.0123456789"

		self.focus()
	
	# set the text to be displayed
	def set_text(self, text):
		self.text = text
		self.curpos = len(text)
		self.repaint()
	
	# when focus received
	def focus(self):
		self.is_in_focus = True
		self.repaint()

	# when focus lost
	def blur(self):
		self.is_in_focus = False
		self.repaint()

	# handles key presses
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
				beep()
		elif(ch == curses.KEY_DC):
			if(self.curpos == len(self.text)):
				beep()
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
				beep()
		elif(ch == curses.KEY_RIGHT):
			if(self.curpos < len(self.text)): 
				self.curpos += 1
			else:
				beep()
		else:
			char = str(chr(ch))
			if(self.charset.find(char) != -1):
				if(not self.numeric or self.numeric_charset.find(char) != -1):
					if(self.maxlen < 0 or self.curpos < self.maxlen-1):					
						self.text = (self.text[0:self.curpos] if self.curpos>0 else "") + char + (self.text[self.curpos:] if self.curpos<len(self.text) else "")
						self.curpos += 1
					else:
						beep()
				else:
					beep()
			else:
				beep()
		
		self.repaint()

	# draws the textfield
	def repaint(self):
		curses.curs_set(self.is_in_focus)
		paint_theme = self.theme
		if(self.is_in_focus and self.focus_theme != None): paint_theme = self.focus_theme
		
		self.parent.addstr(self.y, self.x, " " * self.width, paint_theme)
		
		n = len(self.text)
		if(n <= self.width):
			self.parent.addstr(self.y, self.x, self.text, paint_theme)
			self.parent.move(self.y, self.x+self.curpos)
		else:
			# TO DO: fix this word-wrap	
			flank = self.width // 2
			start = self.curpos - flank
			end = self.curpos + flank

			if(start < 0):
				delta = abs(start)
				start += delta
				end += delta				
			elif(end > n):
				delta = end - n
				start -= delta
				end -= delta
			
			vtext = self.text[start:end]
			vcurpos = self.curpos - start

			self.parent.addstr(self.y, self.x, vtext, paint_theme)
			self.parent.move(self.y, self.x+vcurpos)
		
	# returns the text of the textfield
	def __str__(self):
		return self.text