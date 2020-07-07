# ---------------------------------------------------------------------------------------------
#  Copyright (c) Akash Nag. All rights reserved.
#  Licensed under the MIT License. See LICENSE.md in the project root for license information.
# ---------------------------------------------------------------------------------------------

# This module handles all utility functions

from ash.core import *
from ash.gui.cursorPosition import *

# <---------------------- key bindings --------------------------->

# check if Caps Lock is on/off
def is_capslock_on():
	x = int(subprocess.getoutput("xset q | grep LED")[65])
	return(True if x==1 else False)

# check if a Ctrl+Key combination was pressed
def is_ctrl(ch, key):
	key = str(key).upper()
	sch = str(curses.keyname(ch))
	return(True if sch == "b'^" + key + "'" else False)

# check if either a Ctrl+Key or a Function-key has been pressed
def is_ctrl_or_func(ch):
	sch = str(curses.keyname(ch))
	return(True if sch.startswith("b'KEY_F(") or sch.startswith("b'^") or (sch.startswith("b'k") and sch.endswith("5'")) else False)

# check if a particular function key has been pressed
def is_func(ch, k=None):
	sch = str(curses.keyname(ch))
	if(k == None):
		return(True if sch.startswith("b'KEY_F(") else False)
	else:
		return(True if sch == "b'KEY_F(" + str(k) + ")'" else False)

def get_func_key(ch):
	if(not is_func(ch)):
		return None
	else:
		sch = str(curses.keyname(ch))
		if(sch[9] == ")"):
			return int(sch[8])
		else:
			return int(sch[8:10])

# check if Enter or Ctrl+J has been pressed
def is_newline(ch):
	return (ch == curses.KEY_ENTER or is_ctrl(ch, "J"))

# check if Tab or Ctrl+I has been pressed
def is_tab(ch):
	return (ch == curses.KEY_STAB or is_ctrl(ch, "I"))

# check if Ctrl+Arrow has been pressed
def is_ctrl_arrow(ch, arrow = None):
	sch = str(curses.keyname(ch))
	if(arrow == None):
		return (True if (sch == "b'kUP5'" or sch == "b'kDN5'" or sch == "b'kLFT5'" or sch == "b'kRIT5'") else False)
	else:
		sarrow = str(arrow).upper()
		
		if(sch == "b'kUP5'" and sarrow == "UP"):
			return True
		elif(sch == "b'kDN5'" and sarrow == "DOWN"):
			return True
		elif(sch == "b'kLFT5'" and sarrow == "LEFT"):
			return True
		elif(sch == "b'kRIT5'" and sarrow == "RIGHT"):
			return True
		else:
			return False

def is_keyname(ch, name):
	sch = str(curses.keyname(ch))
	if(sch == "b'k" + name + "'"):
		return True
	else:
		return False

# <------------------------- other functions ---------------------->


# check if selection-start is before selection-end or vice-versa
# i.e. check if selection is forwards from the cursor, or backwards
def is_start_before_end(start, end):
	if(start.y == end.y and start.x < end.x): return True
	if(start.y < end.y): return True
	return False


def get_center_coords(app, elem_height, elem_width):
	return ((app.screen_height - elem_height) // 2, (app.screen_width - elem_width) // 2)

def beep():
	curses.beep()

def get_horizontal_cursor_position(text, curpos, tab_size):
	ptext = text[0:curpos]
	x = 0	
	for c in ptext:
		if(c == "\t"):
			x += (tab_size - (x % tab_size))
		else:
			x += 1
	return x

def get_message_dimensions(msg):
	mlines = msg.count("\n") + 1
	data = msg.split("\n")
	mlen = 0
	for line in data:
		if(len(line) > mlen):
			mlen = len(line)
	return (mlines, mlen)

def get_relative_file_title(project_dir, filename):
	pos = project_dir.rfind("/")
	if(pos == 0):
		return filename[pos:]
	else:
		return filename[pos+1:]

def str_reverse(text):
	rtext = ""
	n = len(text)
	for i in range(n):
		rtext += text[n-i-1]
	return rtext

def soft_wrap(text, width, break_words):
	# assumes 'text' does not contain newlines
	if("\n" in text): raise(Exception("Newline found during wrap operation!"))

	separators = "~!@#$%^&*()-=+\\|[{]};:,<.>/? \t\n"
	text += "\n"		# append newline to make life easier
	n = len(text) - 1
	lines = list()
	while(n > width):
		sub = text[0:width]
		if(sub[-1] in separators or text[width] == "\n"):
			# we are lucky to have the line end in a separator
			lines.append(sub)
			text = text[width:]
			n -= width
			if(text == "\n"): text = ""
		else:
			ls = len(sub)
			rsub = str_reverse(sub)
			index = next((i for i, ch in enumerate(rsub) if ch in separators), None)
			if(index == None):
				# no separator found before intended line-break
				if(break_words):
					# breaking words are allowed: switch to hard-wrap
					lines.append(sub)
					text = text[width:]
					n -= width
					if(text == "\n"): text = ""
				else:
					# breaking words are not allowed: find next separator position
					index = next((i for i, ch in enumerate(text) if ch in separators), None)
					# index will never be None bcoz we have appended newline to end
					if(text[index] == "\n"):
						lines.append(text[0:index])
						text = ""
						n = 0
					else:
						sub = text[0:index+1]
						text = text[index+1:]
						lines.append(sub)
						n -= index+1
			else:
				sub = text[0:ls-index]
				lines.append(sub)
				text = text[ls-index:]
				n -= (ls-index)
	
	lines.append(text[0:n])
	return lines

def wrapped(line, width, word_wrap, break_words):
	sub_lines = list()
	if(not word_wrap):
		sub_lines.append(line)
	else:
		sub_lines = soft_wrap(line, width, break_words)
	return sub_lines

def get_wrapped_curpos(sublines, x):
	if(len(sublines) <= 1): return (0,x)

	i = 0
	vpos = -1
	cpos = x
	for l in sublines:
		if(cpos < len(l)):
			vpos = i
			break
		else:
			cpos -= len(l)
		i += 1

	return (vpos, cpos)

def get_rendered_pos(lines, width, hard_wrap, orig_pos, cum_lengths):
	wrapped_current_line = soft_wrap(lines[orig_pos.y], width, hard_wrap)
	offset_y, offset_x = get_wrapped_curpos(wrapped_current_line, orig_pos.x)
	y = cum_lengths[orig_pos.y] + offset_y
	x = offset_x
	rendered_curpos = CursorPosition(y, x)	
	return rendered_curpos


# 01234 l=5
# 567   l=3
# len(sublines)=2, x=5
# i=0, vpos = -1, cpos = 0

# w=10
# 0 (35):= 0, 1, 2, 3 {4}, cl=0		0,1,2,3
# 1 (11):= 0, 1		  {2}, cl=4		4,5
# 2 (5) := 0		  {1}, cl=6		6
# 3 (25):= 0, 1, 2	  {3}, cl=7		7,8,9
# what is the y-pos of 3? = cl[y] = cl[3] = 7+0 or 7+1 or 7+2

def approx_bsearch(num_list, sval):
	lb = 0
	ub = len(num_list) - 1
	while(lb <= ub):
		m = (lb+ub) // 2
		if(sval == num_list[m]):
			return m
		elif(sval < num_list[m]):
			ub = m-1
		else:
			lb = m+1

	# sval lies between r-1 and r, or r and r+1, or r+1 and r+2
	# where r is the return value
	return m

def translate_line_number(line_num, cum_lengths):
	bpos = approx_bsearch(cum_lengths, line_num)
	# line_num lies btween bpos-1 and bpos
	
	# [0] 0,1,2			{3}	cl=0
	# [1] 3,4			{2}	cl=3
	# [2] 5,6,7*,8,9	{5}	cl=5
	# [3] 10,11,12		{3}	cl=10
	# [4] 13			{1}	cl=13

	# line=7 should translate to " ", bpos = 3, cl[bpos] = 10; line < cl (col=3)

	# [0] 0				{1} cl=0
	# [1] 1				{1} cl=1
	# [2] 2				{1} cl=2

	# line=1 should translate to "2", bpos = 1, cl[bpos] = 1; line = cl (col=1)

	if(line_num == cum_lengths[bpos]):
		return str(bpos+1)
	else:
		return ""

def should_highlight(cur_row, line_num, cum_lengths, last_printed):
	if(cur_row == line_num): return True
	
	lower = cum_lengths[last_printed - 1]
	cb = cum_lengths[last_printed] - cum_lengths[last_printed - 1]
	upper = lower + cb - 1

	if(cur_row >= lower and cur_row <= upper):
		return True
	else:
		return False