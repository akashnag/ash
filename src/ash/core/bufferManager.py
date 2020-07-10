# ---------------------------------------------------------------------------------------------
#  Copyright (c) Akash Nag. All rights reserved.
#  Licensed under the MIT License. See LICENSE.md in the project root for license information.
# ---------------------------------------------------------------------------------------------

# This module implements the Buffer Management Interface

from ash.core import *
from ash.core.logger import *
from ash.gui.cursorPosition import *
from ash.core.editHistory import *
from ash.formatting.syntaxHighlighting import *

BACKUP_FREQUENCY_SIZE	= 16		# backup after every 16 edits
HISTORY_FREQUENCY_SIZE	= 8			# undo: every 8 edit operations

class Buffer:
	def __init__(self, manager, id, filename = None, encoding = "utf-8", newline = "\n", has_backup = False):
		self.manager = manager
		self.id = id
		self.filename = filename
		self.encoding = encoding
		self.editors = list()
		self.display_name = None

		self.backup_edit_count = 0
		self.undo_edit_count = 0
		self.last_curpos = CursorPosition(0,0)
		self.last_called = None
		
		if(self.filename == None):
			self.lines = list()
			self.lines.append("")
			self.save_status = False
			self.backup_file = None
			self.display_name = "untitled-" + str(self.id + 1)
			self.formatter = SyntaxHighlighter(self.display_name)
		else:
			if(has_backup):
				self.backup_file = get_file_directory(self.filename) + "/.ash.b-" + get_file_title(self.filename)
				self.read_file_from_disk(True)
			else:
				self.read_file_from_disk()			
			self.formatter = SyntaxHighlighter(self.filename)
		
		self.history = EditHistory(self.lines, CursorPosition(0,0))
		self.newline = newline		

	def set_encoding(self, encoding):
		self.encoding = encoding

	def set_newline(self, newline):
		self.newline = newline
	
	def attach_editor(self, editor):
		if(editor not in self.editors): self.editors.append(editor)
		
	def detach_editor(self, editor):
		self.editors.remove(editor)

	def has_file(self):
		return (False if self.filename == None else True)

	def do_undo(self):
		if(self.undo_edit_count > 0): 		# add the latest change forcefully
			self.history.add_change(self.lines, self.last_curpos)
			self.undo_edit_count = 0

		hdata = self.history.undo()
		if(hdata == None):
			beep()
		else:
			self.lines = copy.copy(hdata.data)
			for ed in self.editors:
				ed.curpos = copy.copy(hdata.curpos)

	def do_redo(self):
		hdata = self.history.redo()
		if(hdata == None):
			beep()
		else:
			self.lines = copy.copy(hdata.data)
			for ed in self.editors:
				ed.curpos = copy.copy(hdata.curpos)

	def update(self, curpos, caller):			# must be called after every edit made
		self.save_status = False
		
		if(self.backup_file != None and self.backup_edit_count >= BACKUP_FREQUENCY_SIZE):
			self.make_backup()
			self.backup_edit_count = 0
		else:
			self.backup_edit_count += 1

		if(self.undo_edit_count >= HISTORY_FREQUENCY_SIZE):
			self.history.add_change(self.lines, curpos)
			self.undo_edit_count = 0
		else:
			self.undo_edit_count += 1
		
		for ed in self.editors:
			if(ed != caller): ed.notify_update()

		self.last_curpos = curpos
		self.last_caller = caller

	def major_update(self, curpos, caller, make_backup = False):
		self.save_status = False
		if(make_backup): 
			self.make_backup()
			self.backup_edit_count = 0
		else:
			self.backup_edit_count += 1
		
		self.history.add_change(self.lines, curpos)
		self.undo_edit_count = 0
		
		for ed in self.editors:
			if(ed != caller): ed.notify_update()

		self.last_curpos = curpos
		self.last_caller = caller
	
	def write_to_disk(self, filename = None):
		if(self.filename == None and filename == None): raise(Exception("Error 1: buffer.write_to_disk()"))
		if(filename != None): self.filename = filename		# update filename even if filename has changed
		
		self.formatter = SyntaxHighlighter(self.filename)
		self.display_name = None

		data = self.get_data()
		textFile = codecs.open(self.filename, "w", self.encoding)
		textFile.write(data)
		textFile.close()
		self.save_status = True
		self.backup_file = get_file_directory(self.filename) + "/.ash.b-" + get_file_title(self.filename)

		self.backup_edit_count = 0
		self.undo_edit_count = 0

		return self.manager.merge_if_required(self.id)

	def is_editor_attached(self, editor):
		return (True if editor in self.editors else False)

	def is_empty(self):
		if(len(self.lines) == 1 and len(self.lines[0]) == 0):
			return True
		else:
			return False

	def get_loc(self):
		nlines = len(self.lines)
		sloc = 0
		
		for x in self.lines:
			if(len(x.strip()) == 0):
				sloc += 1

		return (nlines, nlines - sloc)

	def destroy(self):
		if(self.backup_file != None and os.path.isfile(self.backup_file)): 
			os.remove(self.backup_file)			# remove backup safely

	def get_data(self):
		return self.newline.join(self.lines)

	def reload_from_disk(self):					# alias function
		self.read_file_from_disk()
		self.display_name = None

	def get_file_size(self):					# alias function
		return get_file_size(self.filename)

	def get_name(self):
		if(self.filename != None):
			return self.filename
		else:
			return self.display_name

	def can_destroy(self):
		if(self.save_status): return True
		if(self.filename != None): return False
		if(self.is_empty()): return True
		return False

	def format_code(self, text):
		return self.formatter.format_code(text)

	# <------------------- private functions ---------------------->
	def make_backup(self):
		if(self.backup_file == None): return
		data = self.get_data()
		textFile = codecs.open(self.backup_file, "w", self.encoding)
		textFile.write(data)
		textFile.close()

	def read_file_from_disk(self, read_from_backup = False):
		filename = (self.backup_file if read_from_backup else self.filename)

		if(self.manager.is_binary(filename)): raise(Exception("Error: buffer: attempting to read binary file"))

		textFile = codecs.open(filename, "r", self.encoding)
		text = textFile.read()
		textFile.close()
		self.render_data_to_lines(text)
		
		if(not read_from_backup): 
			self.backup_file = get_file_directory(self.filename) + "/.ash.b-" + get_file_title(self.filename)
			self.save_status = True
		else:
			self.save_status = False

		self.backup_edit_count = 0
		self.undo_edit_count = 0
		
		return 0

	def render_data_to_lines(self, text):
		self.lines = list()
		if(len(text) == 0):
			self.lines.append("")
		else:
			lines = text.splitlines()
			for line in lines:
				self.lines.append(line)
			if(text.endswith("\n")): self.lines.append("")


class BufferManager:
	def __init__(self):
		self.buffers = dict()
		self.buffer_count = 0
	
	def create_new_buffer(self, filename = None, encoding = None, newline = "\n", has_backup = False):
		if(self.does_file_have_its_own_buffer(filename)): raise(Exception("Error 5: buffermanager.create_new_buffer()"))
		if(encoding == None):
			if(filename == None or not os.path.isfile(filename)):
				encoding = "utf-8"
			else:
				encoding = predict_file_encoding(filename)
		self.buffers[self.buffer_count] = Buffer(self, self.buffer_count, filename, encoding, newline, has_backup)
		self.buffer_count += 1
		return (self.buffer_count - 1, self.buffers[self.buffer_count - 1])

	def attach_editor(self, buffer_id, editor):
		if(buffer_id >= self.buffer_count):
			raise(Exception("Error 2: buffermanager.attach_editor()"))
		else:
			self.buffers[buffer_id].attach_editor(editor)

	def detach_editor(self, buffer_id, editor):
		if(buffer_id >= self.buffer_count):
			raise(Exception("Error 3: buffermanager.detach_editor()"))
		else:
			self.buffers[buffer_id].detach_editor(editor)

	def __len__(self):
		return self.buffer_count

	def get_name(self, buffer_id):
		if(buffer_id >= self.buffer_count):
			raise(Exception("Error 6: buffermanager.get_name()"))
		else:			
			return self.buffers[buffer_id].get_name()			

	def get_buffer_by_id(self, buffer_id):
		for bid, buffer in self.buffers.items():
			if(bid == buffer_id): return buffer
		return None

	def get_buffer_by_filename(self, filename):
		if(filename == None): return None
		for bid, buffer in self.buffers.items():
			if(buffer.filename == filename): return buffer
		return None

	def does_file_have_its_own_buffer(self, filename):
		if(filename == None): return False
		for bid, buffer in self.buffers.items():
			if(buffer.filename == filename): return True
		return False

	def get_unsaved_count(self):
		count = 0
		for bid, buffer in self.buffers.items():
			if(not buffer.save_status): count += 1
		return count

	def get_unsaved_file_count(self):
		count = 0
		for bid, buffer in self.buffers.items():
			if(buffer.filename != None and not buffer.save_status): count += 1
		return count

	def get_true_unsaved_count(self):
		count = 0
		for bid, buffer in self.buffers.items():
			if(not buffer.save_status):
				if(buffer.filename != None or not buffer.is_empty()): count += 1
		return count

	def can_destroy_after_saving(self):
		for bid, buffer in self.buffers.items():
			if(buffer.filename != None and not buffer.is_empty()): return False
		return True

	def write_all_wherever_possible(self):
		self.write_all(True)
						
	def write_all(self, ignore_errors=False):
		for bid, buffer in self.buffers.items():
			if(not buffer.save_status):
				if(buffer.filename == None):
					if(not ignore_errors): raise(Exception("Error 4: buffermanager.write_all()"))
				else:
					buffer.write_to_disk()

	def destroy(self):
		for bid, buffer in self.buffers.items():
			buffer.destroy()

		self.buffer_count = 0
		self.buffers = dict()

	def merge_if_required(self, child_id):
		# called from child_id on file-save: 
		# check if two buffers have same filename: 
		# if yes, delete them (since child_id has just been saved to file and contains the latest copy)
		# and attach their editors to this

		merge_required = False
		parent_buffer = self.buffers[child_id]
		query_filename = parent_buffer.filename
		merged_ids = list()				# stores IDs of buffers (other than child_id) to be merged with child_id
		
		for bid, buffer in self.buffers.items():
			if(bid != child_id and buffer.filename == query_filename):
				merge_required = True
				merged_ids.append(bid)
		
		if(not merge_required): return False
				
		# attach editors and delete buffers
		for mid in merged_ids:
			# notify editors of the change
			for ed in self.buffers[mid].editors:
				ed.notify_merge(child_id, parent_buffer)
			# attach the editors
			parent_buffer.editors.extend(self.buffers[mid].editors)
			# delete the buffer
			del self.buffers[mid]

		return True

	def get_list(self):
		buffer_list = list()
		for bid, buffer in self.buffers.items():
			buffer_list.append( (bid, buffer.save_status, buffer.get_name()) )
		return buffer_list

	@staticmethod
	def backup_exists(filename):
		if(os.path.isfile(get_file_directory(filename) + "/.ash.b-" + get_file_title(filename))):
			return True
		else:
			return False

	@staticmethod
	def is_binary(filename):
		mt = str(mimetypes.guess_type(filename, strict=False)[0]).lower()
		if(mt.startswith("text/")):
			return False
		else:
			return True