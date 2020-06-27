# ---------------------------------------------------------------------------------------------
#  Copyright (c) Akash Nag. All rights reserved.
#  Licensed under the MIT License. See LICENSE.md in the project root for license information.
# ---------------------------------------------------------------------------------------------

# This module implements the CursorPosition abstraction

from ash.widgets.utils import *
from ash.widgets.utils.utils import *
from ash.widgets.utils.formatting import *

class CursorPosition:
	def __init__(self, y, x):
		self.y = y
		self.x = x

	def __str__(self):
		return "(" + str(self.y+1) + "," + str(self.x+1) + ")"
	
	def real_str(self):
		return "(" + str(self.y) + "," + str(self.x) + ")"