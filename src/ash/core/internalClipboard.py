# ---------------------------------------------------------------------------------------------
#  Copyright (c) Akash Nag. All rights reserved.
#  Licensed under the MIT License. See LICENSE.md in the project root for license information.
# ---------------------------------------------------------------------------------------------

# This module implements the internal clipboard if pyperclip/xclip is unavailable

class InternalClipboard:
	# initialize the buffer to the empty string
	clipboard_buffer = ""

	# copies 'data' to the clipboard
	@classmethod
	def copy(cls, data):
		cls.clipboard_buffer = data

	# returns data stored in the clipboard
	@classmethod
	def paste(cls):
		return cls.clipboard_buffer