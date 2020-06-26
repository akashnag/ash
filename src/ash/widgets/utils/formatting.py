# ---------------------------------------------------------------------------------------------
#  Copyright (c) Akash Nag. All rights reserved.
#  Licensed under the MIT License. See LICENSE.md in the project root for license information.
# ---------------------------------------------------------------------------------------------

# This module handles all text formatting for the application

from ash.widgets.utils import *

# chop off a string if it exceeds maxlen and end it with "..."
def pad_str_max(data, maxlen):
	n = len(data)
	if(n <= maxlen):
		return data
	else:
		return data[0:maxlen-3] + "..."