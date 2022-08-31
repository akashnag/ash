# SPDX-License-Identifier: GPL-2.0-only
#
# /src/ash/core/internalClipboard.py
#
# Copyright (C) 2022-2022  Akash Nag

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