# ---------------------------------------------------------------------------------------------
#  Copyright (c) Akash Nag. All rights reserved.
#  Licensed under the MIT License. See LICENSE.md in the project root for license information.
# ---------------------------------------------------------------------------------------------

# This module implements the CursorPosition abstraction

class CursorPosition:
	def __init__(self, y, x):
		self.y = y
		self.x = x

	# returns a string representation of the cursor position for the user
	def __str__(self):
		return "(" + str(self.y+1) + "," + str(self.x+1) + ")"
	
	# returns the string representation for internal use
	def __repr__(self):
		return "(" + str(self.y) + "," + str(self.x) + ")"