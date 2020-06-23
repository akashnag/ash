# ---------------------------------------------------------------------------------------------
#  Copyright (c) Akash Nag. All rights reserved.
#  Licensed under the MIT License. See LICENSE.md in the project root for license information.
# ---------------------------------------------------------------------------------------------

# This module implements the CursorPosition abstraction

from ash.widgets import *
from ash.widgets.utils.utils import *
from ash.widgets.utils.formatting import *

class CursorPosition:
	def __init__(self, y, x):
		self.y = y
		self.x = x

	def __str__(self):
		#return "Ln " + str(self.y+1) + ", Col " + str(self.x+1)
		return "(" + str(self.y+1) + "," + str(self.x+1) + ")"
