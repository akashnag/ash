# ---------------------------------------------------------------------------------------------
#  Copyright (c) Akash Nag. All rights reserved.
#  Licensed under the MIT License. See LICENSE.md in the project root for license information.
# ---------------------------------------------------------------------------------------------

# This module implements the edit history of a document to realize the undo/redo operations

from ash.core import *

# define the maximum size of the history to be stored (in bytes)
MAX_HISTORY_SIZE	=	65536

# HistoricalData class: encapsulates an editor-state containing:
# (1) data	(2) cursor-position
class HistoricalData:
	def __init__(self, data, curpos):
		self.data = copy.copy(data)
		self.curpos = copy.copy(curpos)

	def size(self):
		return sys.getsizeof(self.data)

# StackNode class: implements a node in a linked-stack
class StackNode:
	def __init__(self, data, link = None, parent = None):
		self.data = data
		self.link = link
		self.parent = parent

# Stack class: implements a standard linked-stack with drop feature (to drop one or more nodes)
class Stack:
	def __init__(self):
		self.top = None
		self.__size = 0

	# pushes data onto the stack
	def push(self, hdata):
		temp = StackNode(hdata, self.top, None)
		if(self.top != None): self.top.parent = temp
		self.top = temp
		self.__size += 1

	# pops the most recently pushed data from the stack
	def pop(self):
		if(self.__size == 0):
			return None
		else:
			data = self.top.data
			self.top = self.top.link
			if(self.top != None): self.top.parent = None
			self.__size -= 1
			return data

	# returns the number of items in the stack
	def length(self):
		return self.__size

	# returns the total memory being used by the stack (in bytes)
	def size(self):
		temp = self.top
		s = 0
		while(temp != None):
			s += temp.data.size()
			temp = temp.link
		return s

	# removes the oldest 'count' items from the stack
	def drop(self, count = 1):
		if(count < 1): return
		count = min([count, self.__size])
		temp = self.top
		for i in range(self.__size - count - 1):
			temp = temp.link
		temp.link = None
		self.__size -= count

# EditHistory class: emcapsulates an interface to implement undo-redo operations
class EditHistory:
	def __init__(self, data, curpos):
		self.stack = Stack()
		self.stack.push(HistoricalData(data, curpos))
		self.present = self.stack.top
		self.depth_from_top = 0
	
	# records a change/edit
	def add_change(self, data, curpos):
		while(self.depth_from_top > 0):
			self.stack.pop()
			self.depth_from_top -= 1
		
		self.stack.push(HistoricalData(data, curpos))
		self.present = self.stack.top

		while(self.stack.size() > MAX_HISTORY_SIZE):
			self.stack.drop()

	# reverts to previous state and returns a copy of the last edit performed
	def undo(self):
		if(self.depth_from_top == self.stack.length() - 1):
			return None
		else:
			self.present = self.present.link
			self.depth_from_top += 1
			return copy.copy(self.present.data)

	# cancels the last undo() performed and returns a copy of the data after redo()
	def redo(self):
		if(self.depth_from_top == 0):
			return None
		else:
			self.present = self.present.parent
			self.depth_from_top -= 1
			return copy.copy(self.present.data)