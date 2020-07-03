# ---------------------------------------------------------------------------------------------
#  Copyright (c) Akash Nag. All rights reserved.
#  Licensed under the MIT License. See LICENSE.md in the project root for license information.
# ---------------------------------------------------------------------------------------------

# This module handles all syntax highlighting

import pygments
import pygments.lexers

from pygments.token import Token
from ash.formatting.colors import *

class SyntaxHighlighter:
	def __init__(self, filename):
		self.reset_file(filename)

	def reset_file(self, filename):
		try:
			self.lexer = pygments.lexers.get_lexer_for_filename(filename)
		except:
			self.lexer = None

	def format_code(self, line, index_start = 0, index_end = -1):
		# return a list of tuples (text, style)
		# style = gc(SOMETHING) or curses.A_BOLD | gc(SOMETHING)
		pass