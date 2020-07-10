# ---------------------------------------------------------------------------------------------
#  Copyright (c) Akash Nag. All rights reserved.
#  Licensed under the MIT License. See LICENSE.md in the project root for license information.
# ---------------------------------------------------------------------------------------------

# This module handles all utility functions

from ash.utils import *

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

def str_reverse(text):
	rtext = ""
	n = len(text)
	for i in range(n):
		rtext += text[n-i-1]
	return rtext

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