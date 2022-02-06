# ---------------------------------------------------------------------------------------------
#  Copyright (c) Akash Nag. All rights reserved.
#  Licensed under the MIT License. See LICENSE.md in the project root for license information.
# ---------------------------------------------------------------------------------------------

# This module handles all utility functions

from ash.core.ashException import AshException
from ash.utils import *

import re
import select
import sys
import threading
import multiprocessing
import time
import termios

def is_enclosed(y, x, area):
	area_y, area_x, area_height, area_width = area
	if(y >= area_y and y < area_y + area_height and x >= area_x and x < area_x + area_width):
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

# finds the (y,x) for placing a window centrally on a screen
def get_center_coords(app, elem_height, elem_width):
	if(elem_height > (app.screen_height-2) or elem_width > (app.screen_width-1)):
		raise(AshException("Dialog exceeds screen dimensions"))
		
	return ((app.screen_height - elem_height) // 2, (app.screen_width - elem_width) // 2)

# plays the default system bell sound
def beep():
	curses.beep()

# calculate the horizontal cursor position given its original position in a text and a specified tab-size
def get_horizontal_cursor_position(text, curpos, tab_size):
	ptext = text[0:curpos]
	x = 0	
	for c in ptext:
		if(c == "\t"):
			x += (tab_size - (x % tab_size))
		else:
			x += 1
	return x

# get the maximum height and width of a message
def get_message_dimensions(msg):
	mlines = msg.count("\n") + 1
	data = msg.split("\n")
	mlen = 0
	for line in data:
		if(len(line) > mlen):
			mlen = len(line)
	return (mlines, mlen)

# perform a binary search
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

# translate actual line number to displayed line number
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

# check if the given line-number should be highlighted as the active/current line
def should_highlight(cur_row, line_num, cum_lengths, last_printed):
	if(cur_row == line_num): return True
	
	try:
		lower = cum_lengths[last_printed - 1]
		cb = cum_lengths[last_printed] - cum_lengths[last_printed - 1]
		upper = lower + cb - 1

		if(cur_row >= lower and cur_row <= upper):
			return True
		else:
			return False
	except:
		return False

# expand tabs in a list of lines
def expand_tabs_in_lines(lines, tab_size):
	elines = list()
	for l in lines:
		elines.append(l.expandtabs(tab_size))
	return elines

# return a list of indexes where 'delim' occurs in 'string'
def get_delim_positions(string, delim):
	if(delim == None or string == None): return None
	n = len(string)
	l = len(delim)
	if(n == 0 or l == 0): return None
	pos = list()
	for i in range(n-l+1):
		if(string[i:i+l] == delim):
			pos.append(i)
	return pos

# perform syntax highlighting for a range of lines
def get_format_list_for_lines(buffer, rendered_lines, line_start, line_end, nlines):
	format_list = list()
	for i in range(line_start, line_end):
		if(i >= nlines): break
		fc = buffer.format_code(rendered_lines[i])
		format_list.append(fc)
	return format_list

# extract a portion of the syntax-highlighting for the visible portion of a line
def get_sub_lex_list(data, start, end):
	sub_list = list()
	started = False
	for begin, token_style, value in data:
		x = len(value) - 1 + begin
		if(not started and begin <= start and x >= start):
			if(x >= end):
				sub_list.append( (0, token_style, value[start-begin:end-begin]  ))
				return sub_list
			else:
				started = True
				sub_list.append( (0, token_style, value[start-begin:]) )
		elif(started):
			if(x >= end):
				sub_list.append( (begin-start, token_style, value[0:end-begin+1]  ))
				return sub_list
			else:
				sub_list.append( (begin - start, token_style, value) )
	return sub_list

# find a regex
def find_regex(text, regex):
	match_obj = re.search(regex, text)

	if(match_obj != None):
		span = match_obj.span()
		start = span[0]
		end = span[1]
		mtext = text[start:end]
		return start
	else:
		return -1

# find a whole word
def find_whole_word(text, search):
	sep_list = "[]{}()+-*/%=<>.,/?;:'\"!|&^ "
	separators = "[" + re.escape(sep_list) + "]"
	x = search
	while(x[0] in sep_list): x = x[1:]
	while(x[-1] in sep_list): x = x[:-1]

	s = re.escape(x)
	regex = "^"+s+separators
	regex += "|"+separators+s+"$"
	regex += "|"+"^"+s+"$"
	regex += "|"+separators+s+separators

	match_obj = re.search(regex, text)

	if(match_obj != None):
		span = match_obj.span()
		start = span[0]
		end = span[1]
		mtext = text[start:end]
		pos = mtext.find(search)
		#mtext = text[start+pos:start+pos+len(search)]
		return start+pos
	else:
		return -1


# read data from stdin pipe
#def read_piped_data():
#	data = ""
#	while(not sys.stdin.isatty()):
#		x = sys.stdin.read(1)
#		if(len(x) == 0): break
#		data += x
#	return (data if len(data) > 0 else None)

"""
def read_char_from_stdin(data):
	data.append(sys.stdin.read(1))

def read_piped_data():
	data = ""
	while(sys.stdin in select.select([sys.stdin,],[],[],0.0)[0]):
		incoming = []

		t1 = multiprocessing.Process(target=read_char_from_stdin, args=(incoming,))
		t1.daemon = True
		t1.start()
		time.sleep(0.01)
		t1.terminate()
		
		if(len(incoming) == 0): break
		data += incoming[0]

	sys.stdin = open("/dev/tty")
	
	data += "\nProcessing done!"
	return (data if len(data) > 0 else None)
"""

"""
def read_piped_data():
	data = ""
	while(sys.stdin in select.select([sys.stdin,],[],[],0.0)[0]):
		x = sys.stdin.read(1)
		if(len(x) == 0): break
		data += x

	sys.stdin = open("/dev/tty")
	return (data if len(data) > 0 else None)
"""