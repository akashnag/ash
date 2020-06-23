# ---------------------------------------------------------------------------------------------
#  Copyright (c) Akash Nag. All rights reserved.
#  Licensed under the MIT License. See LICENSE.md in the project root for license information.
# ---------------------------------------------------------------------------------------------

# This module implements the FileData abstraction

from ash.widgets import *
from ash.widgets.utils.utils import *
from ash.widgets.utils.formatting import *
from ash.widgets.cursorPosition import *

class FileData:
	def __init__(self, filename=None, buffer=None, curpos=None, save_status=True, selection_mode=False, sel_start=None, sel_end=None, encoding="utf-8", tab_size = 4):
		self.has_been_allotted_file = (False if filename == None else True)
		self.filename = copy.copy(filename)

		self.tab_size = tab_size
		self.encoding = encoding
		self.selection_mode = selection_mode
		self.sel_start = (CursorPosition(0,0) if sel_start==None else copy.copy(sel_start))
		self.sel_end = (CursorPosition(0,0) if sel_end==None else copy.copy(sel_end))
		self.curpos = (CursorPosition(0,0) if curpos==None else copy.copy(curpos))
		self.save_status = (False if filename == None else save_status)

		if(buffer == None and filename == None):
			self.buffer = ""
		elif(buffer == None and filename != None):
			self.buffer = self.__read_from_file(filename)
		else:
			self.buffer = copy.copy(buffer)


	# reloads the file from disk
	def reload(self):
		if(not self.has_been_allotted_file): return

		self.buffer = self.__read_from_file(self.filename)
		self.selection_mode = False
		self.sel_start = CursorPosition(0,0)
		self.sel_end = CursorPosition(0,0)
		self.curpos = CursorPosition(0,0)
		self.save_status = True

	def __read_from_file(self, filename):
		if(not os.path.isfile(filename)): 
			self.save_status = False
			return ""

		textFile = open(filename, "rt")
		data = textFile.read()
		textFile.close()
		return data

	def is_filed(self):
		return self.has_been_allotted_file

	def save_to_file(self, filename):
		textFile = open(self.filename, "wt")
		textFile.write(self.buffer)
		textFile.close()
		self.filename = filename
		self.has_been_allotted_file = True
		self.save_status = save_status