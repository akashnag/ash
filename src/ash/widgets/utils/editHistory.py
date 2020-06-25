# ---------------------------------------------------------------------------------------------
#  Copyright (c) Akash Nag. All rights reserved.
#  Licensed under the MIT License. See LICENSE.md in the project root for license information.
# ---------------------------------------------------------------------------------------------

# This module implements the edit history of a document to realize the undo/redo operations

import copy

MAX_HISTORY_SIZE	=	65536		# max history size per editor (in bytes)

class HistoricalData:
	def __init__(self, data, curpos):
		self.data = copy.copy(data)
		self.curpos = copy.copy(curpos)

	def size(self):
		return len(self.data)

class StackNode:
	def __init__(self, data, link = None, parent = None):
		self.data = data
		self.link = link
		self.parent = parent

class Stack:
	def __init__(self):
		self.top = None
		self.__size = 0

	def push(self, hdata):
		temp = StackNode(hdata, self.top, None)
		if(self.top != None): self.top.parent = temp
		self.top = temp
		self.__size += 1

	def pop(self):
		if(self.__size == 0):
			return None
		else:
			data = self.top.data
			self.top = self.top.link
			if(self.top != None): self.top.parent = None
			self.__size -= 1
			return data

	def length(self):
		return self.__size

	def size(self):
		temp = self.top
		s = 0
		while(temp != None):
			s += temp.data.size()
			temp = temp.link
		return s

	def drop(self, count = 1):
		if(count < 1): return
		count = min([count, self.size])
		temp = self.top
		for i in range(self.size - count - 1):
			temp = temp.link
		temp.link = None
		self.__size -= count

class EditHistory:
	def __init__(self, data, curpos):
		self.stack = Stack()
		self.stack.push(HistoricalData(data, curpos))
		self.present = self.stack.top
		self.depth_from_top = 0
		
	def add_change(self, data, curpos):
		while(self.depth_from_top > 0):
			self.stack.pop()
			self.depth_from_top -= 1
		
		self.stack.push(HistoricalData(data, curpos))
		self.present = self.stack.top

		while(self.stack.size() > MAX_HISTORY_SIZE):
			self.stack.drop()

	def undo(self):
		if(self.depth_from_top == self.stack.length() - 1):
			return None
		else:
			self.present = self.present.link
			self.depth_from_top += 1
			return copy.copy(self.present.data)

	def redo(self):
		if(self.depth_from_top == 0):
			return None
		else:
			self.present = self.present.parent
			self.depth_from_top -= 1
			return copy.copy(self.present.data)