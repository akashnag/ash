# SPDX-License-Identifier: GPL-2.0-only
#
# /src/ash/core/ashException.py
#
# Copyright (C) 2022-2022  Akash Nag

# This module implements the custom exception class

from ash.core.logger import *

class AshException(Exception):
	def __init__(self, error_msg):
		super().__init__(error_msg)
		self.error_msg = error_msg
		log_error(self.error_msg)

	def __str__(self):
		return self.error_msg

class AshFileReadAbortedException(Exception):
	def __init__(self, filename):
		self.error_msg = f"Error in reading file: {filename}"
		super().__init__(self.error_msg)
		log_error(self.error_msg)

	def __str__(self):
		return self.error_msg
