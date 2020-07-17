# ---------------------------------------------------------------------------------------------
#  Copyright (c) Akash Nag. All rights reserved.
#  Licensed under the MIT License. See LICENSE.md in the project root for license information.
# ---------------------------------------------------------------------------------------------

# This module handles all syntax highlighting

from ash.formatting import *
from ash.formatting.colors import *

import pygments
import pygments.lexers
from pygments.token import Token

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
style_map[Token.Literal.String.Backtick] = "global-code"
style_map[Token.Generic.Strong] = "global-keyword"
style_map[Token.Generic.Heading] = "global-function"
style_map[Token.Generic.Subheading] = "global-function"
style_map[Token.Name.Tag] = "global-keyword"
style_map[Token.Name.Attribute] = "global-function"
# <----------------------------------------------------------------->

# SyntaxHighlighter class: stylizes text according to its language
class SyntaxHighlighter:
	def __init__(self, filename):
		self.reset_file(filename)

	# sets filename and initializes lexer
	def reset_file(self, filename):
		try:
			self.lexer = pygments.lexers.get_lexer_for_filename(filename)
			if(filename.lower().endswith(".txt")): self.lexer = None			
		except:
			self.lexer = None

	# return a list of tuples (index, text, style)
	# style = gc(SOME_COLOR_PAIR)
	def format_code(self, line):
		styles = list()
		
		if(self.lexer == None):
			styles.append( (0, gc("global-default"), line) )
			return styles
		
		tokens = self.lexer.get_tokens_unprocessed(line)
		for (index, token_type, value) in tokens:
			styles.append( (int(index), self.get_style(token_type), str(value)) )

		return styles

	# returns the assigned style for a particular token-type
	def get_style(self, token_type):
		style = style_map.get(token_type)
		if(style == None):
			return gc("global-default")
		else:
			return gc(style)