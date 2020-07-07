# ---------------------------------------------------------------------------------------------
#  Copyright (c) Akash Nag. All rights reserved.
#  Licensed under the MIT License. See LICENSE.md in the project root for license information.
# ---------------------------------------------------------------------------------------------

# This module handles all syntax highlighting

import pygments
import pygments.lexers

from pygments.token import Token
from ash.formatting.colors import *

# <------------------- style mapping ---------------------->
style_map = dict()

style_map[Token.Keyword] = "global-keyword"
style_map[Token.Comment.Single] = "global-comment"
style_map[Token.Punctuation] = "global-punctuation"
style_map[Token.Text] = "global-default"
style_map[Token.Error] = "global-error"
style_map[Token.Literal.String.Single] = "global-string"
style_map[Token.Literal.String.Double] = "global-string"
style_map[Token.Name] = "global-variable"
style_map[Token.Name.Function] = "global-function"
style_map[Token.Literal.Number.Integer] = "global-integer"
style_map[Token.Literal.Number.Float] = "global-float"
style_map[Token.Operator] = "global-operator"
style_map[Token.Name.Builtin] = "global-builtin-function"
style_map[Token.Name.Builtin.Pseudo] = "global-builtin-constant"
style_map[Token.Name.Namespace] = "global-namespace"
style_map[Token.Keyword.Namespace] = "global-keyword"

class SyntaxHighlighter:
	def __init__(self, filename):
		self.reset_file(filename)

	def reset_file(self, filename):
		try:
			self.lexer = pygments.lexers.get_lexer_for_filename(filename)
		except:
			self.lexer = None

	def format_code(self, line):
		# return a list of tuples (index, text, style)
		# style = gc(SOMETHING)
		styles = list()
		
		if(self.lexer == None):
			styles.append( (0, line, gc("global-default")) )
			return styles
		
		tokens = self.lexer.get_tokens_unprocessed(line)
		for (index, token_type, value) in tokens:
			styles.append( (int(index), str(value), self.get_style(token_type)) )

		return styles

	def get_style(self, token_type):
		style = style_map.get(token_type)
		if(style == None):		
			return gc("global-default")
		else:
			return gc(style)