# ---------------------------------------------------------------------------------------------
#  Copyright (c) Akash Nag. All rights reserved.
#  Licensed under the MIT License. See LICENSE.md in the project root for license information.
# ---------------------------------------------------------------------------------------------

# This module handles all text formatting for the application

from ash.widgets.utils import *

# right-align a given string
def pad_left_str(data, width):
	sdata = str(data)
	n = len(sdata)
	if(n < width):
		return (" " * (width-n)) + sdata
	else:
		return sdata

# left-align a given string
def pad_right_str(data, width):
	sdata = str(data)
	n = len(sdata)
	if(n < width):
		return sdata + (" " * (width-n))
	else:
		return sdata

# center align a given string
def pad_center_str(str, maxlen):
	if(len(str) >= maxlen):
		return str
	else:
		pad = (maxlen - len(str)) // 2
		return (" " * pad) + str + (" " * pad)

# chop off a string if it exceeds maxlen and end it with "..."
def pad_str_max(data, maxlen):
	n = len(data)
	if(n <= maxlen):
		return data
	else:
		return data[0:maxlen-3] + "..."