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
from ash.formatting.formatting import *

BACKUP_FREQUENCY_SIZE	= 16		# backup after every 16 edits
HISTORY_FREQUENCY_SIZE	= 8			# undo: every 8 edit operations

# Buffer class: encapsulates a single buffer/file
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
				self.backup_file = os.path.dirname(self.filename) + "/.ash.b-" + get_file_title(self.filename)
				self.read_file_from_disk(True)
			else:
				self.read_file_from_disk()			
			self.formatter = SyntaxHighlighter(self.filename)
		
		self.history = EditHistory(self.lines, CursorPosition(0,0))
		self.newline = newline
		if(self.encoding == None): self.encoding = "utf-8"

	# set the text encoding for the buffer
	def set_encoding(self, encoding):
		self.encoding = encoding

	# set the newline character to be used
	def set_newline(self, newline):
		self.newline = newline
	
	# attach an editor to the list of editors mapped to this buffer
	def attach_editor(self, editor):
		if(editor not in self.editors): self.editors.append(editor)
		
	# remove an attached editor from the list of editors
	def detach_editor(self, editor):
		self.editors.remove(editor)

	# checks to see if an editor is attached to this buffer
	def is_editor_attached(self, editor):
		return (True if editor in self.editors else False)

	# returns True if this buffer has been allocated a file on disk
	def has_file(self):
		return (False if self.filename == None else True)

	# revert the buffer to its previous state
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
				ed.notify_update()

	# revert the buffer to its previous state by cancelling the last do_undo() operation
	def do_redo(self):
		hdata = self.history.redo()
		if(hdata == None):
			beep()
		else:
			self.lines = copy.copy(hdata.data)
			for ed in self.editors:
				ed.curpos = copy.copy(hdata.curpos)
				ed.notify_update()

	# keeps track of the number of edit operations performed on the buffer
	# this is called after every edit by the editor
	def update(self, curpos, caller):
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

	# same as update() but forces the buffer to save changes to its edit-history,
	# and to make a backup if desired
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
		caller.notify_self_update()
	
	def decode_unicode(self):
		if(self.undo_edit_count > 0): 		# add the latest change forcefully
			self.history.add_change(self.lines, self.last_curpos)
			self.undo_edit_count = 0

		for index, line in enumerate(self.lines):
			dec_line = get_unicode_encoded_line(line)
			sub_lines = dec_line.splitlines()			# if they contained newlines
			self.lines.pop(index)
			for i in range(len(sub_lines)-1, -1, -1):
				self.lines.insert(index, sub_lines[i])
			self.encoding = "utf-8"

		for ed in self.editors:
			ed.notify_update()
	
	# writes out the buffer to a file on disk
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
		self.backup_file = os.path.dirname(self.filename) + "/.ash.b-" + get_file_title(self.filename)

		self.backup_edit_count = 0
		self.undo_edit_count = 0
		add_opened_file_to_record(self.filename)

		return self.manager.merge_if_required(self.id)

	# checks to see if the buffer contains no data
	def is_empty(self):
		if(len(self.lines) == 1 and len(self.lines[0]) == 0):
			return True
		else:
			return False

	# returns the number of non-empty lines in the buffer
	def get_loc(self):
		nlines = len(self.lines)
		sloc = 0
		
		for x in self.lines:
			if(len(x.strip()) == 0):
				sloc += 1

		return (nlines, nlines - sloc)

	# returns the entire data (all lines) of the buffer as a single string
	def get_data(self):
		return self.newline.join(self.lines)

	# reloads the file from disk
	def reload_from_disk(self):
		if(self.filename != None):
			self.read_file_from_disk()
			self.display_name = None

	# returns the size of the assigned file
	def get_file_size(self):
		return get_file_size(self.filename)

	# returns the name to be displayed by the application:
	# which will either be its filename (if assigned) or a temporary buffer-name
	def get_name(self):
		if(self.filename != None):
			return self.filename
		else:
			return self.display_name

	# performs a syntax-highlighting of the given string using the assigned formatter
	def format_code(self, text):
		return self.formatter.format_code(text)

	# checks if buffer can be safely destroyed without prompting the user about saving changes
	def can_destroy(self):
		if(self.save_status): return True
		if(self.filename != None): return False
		if(self.is_empty()): return True
		return False
	
	# removes any backup files if they exist, called when user deliberately discards unsaved changes
	def destroy(self):
		if(self.backup_file != None and os.path.isfile(self.backup_file)): 
			os.remove(self.backup_file)

	# <------------------- private functions ---------------------->

	# makes a backup of the data
	def make_backup(self):
		if(self.backup_file == None): return
		data = self.get_data()
		textFile = codecs.open(self.backup_file, "w", self.encoding)
		textFile.write(data)
		textFile.close()

	# reads data from the assigned file on disk; optionally from a backup file instead
	def read_file_from_disk(self, read_from_backup = False):
		filename = (self.backup_file if read_from_backup else self.filename)

		if(self.manager.is_binary(filename)): raise(Exception("Error: buffer: attempting to read binary file"))

		if(not os.path.isfile(filename)):
			textFile = codecs.open(filename, "w", self.encoding)
			textFile.close()

		try:
			textFile = codecs.open(filename, "r", self.encoding)
			text = textFile.read()
			textFile.close()
		except:
			raise(Exception("error reading file: " + filename))
			raise

		self.render_data_to_lines(text)
		
		if(not read_from_backup): 
			self.backup_file = os.path.dirname(self.filename) + "/.ash.b-" + get_file_title(self.filename)
			self.save_status = True
		else:
			self.save_status = False

		self.backup_edit_count = 0
		self.undo_edit_count = 0
		
		if(not read_from_backup): add_opened_file_to_record(self.filename)
		return 0

	# splits the raw-data (read from a file) into separate lines
	def render_data_to_lines(self, text):
		self.lines = list()
		if(len(text) == 0):
			self.lines.append("")
		else:
			lines = text.splitlines()
			for line in lines:
				self.lines.append(line)
			if(text.endswith("\n")): self.lines.append("")

# Buffer Manager class: for keeping track of the list of all active buffers
class BufferManager:
	def __init__(self):
		self.buffers = dict()
		self.buffer_count = 0
	
	# creates a new buffer: either blank or from a file on disk
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

	# map an editor to a buffer specified by its buffer ID
	def attach_editor(self, buffer_id, editor):
		if(buffer_id >= self.buffer_count):
			raise(Exception("Error 2: buffermanager.attach_editor()"))
		else:
			self.buffers[buffer_id].attach_editor(editor)

	# removes an editor-mapping from a buffer specified by its buffer ID
	def detach_editor(self, buffer_id, editor):
		if(buffer_id >= self.buffer_count):
			raise(Exception("Error 3: buffermanager.detach_editor()"))
		else:
			self.buffers[buffer_id].detach_editor(editor)

	# returns the number of buffers currently active
	def __len__(self):
		return self.buffer_count

	# returns the display name of the specified buffer
	def get_name(self, buffer_id):
		if(buffer_id >= self.buffer_count):
			raise(Exception("Error 6: buffermanager.get_name()"))
		else:			
			return self.buffers[buffer_id].get_name()			

	# returns a buffer given its ID
	def get_buffer_by_id(self, buffer_id):
		for bid, buffer in self.buffers.items():
			if(bid == buffer_id): return buffer
		return None

	# returns a buffer given its associated filename
	def get_buffer_by_filename(self, filename):
		if(filename == None): return None
		for bid, buffer in self.buffers.items():
			if(buffer.filename == filename): return buffer
		return None

	# checks to see if a file already has an associated buffer
	def does_file_have_its_own_buffer(self, filename):
		if(filename == None): return False
		for bid, buffer in self.buffers.items():
			if(buffer.filename == filename): return True
		return False

	# returns the number of buffers with unsaved changes
	def get_unsaved_count(self):
		count = 0
		for bid, buffer in self.buffers.items():
			if(not buffer.save_status): count += 1
		return count

	# returns the number of buffers (with files) which have unsaved changes
	def get_unsaved_file_count(self):
		count = 0
		for bid, buffer in self.buffers.items():
			if(buffer.filename != None and not buffer.save_status): count += 1
		return count

	# returns the number of buffers which can be closed without saving
	def get_true_unsaved_count(self):
		count = 0
		for bid, buffer in self.buffers.items():
			if(not buffer.save_status):
				if(buffer.filename != None or not buffer.is_empty()): count += 1
		return count

	# writes all buffers to disk if they have an associated file
	def write_all_wherever_possible(self):
		self.write_all(True)
						
	# writes all buffers to disk
	def write_all(self, ignore_errors=False):
		for bid, buffer in self.buffers.items():
			if(not buffer.save_status):
				if(buffer.filename == None):
					if(not ignore_errors): raise(Exception("Error 4: buffermanager.write_all()"))
				else:
					buffer.write_to_disk()

	# destroy all buffers, reset counter
	def destroy(self):
		for bid, buffer in self.buffers.items():
			buffer.destroy()

		self.buffer_count = 0
		self.buffers = dict()

	# merge any buffers with same filenames (e.g. when both have the same filename after a save operation)
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

	# returns information about active buffers as a list of 3-tuples(buffer-ID, save-status, buffer-name)
	def get_list(self):
		buffer_list = list()
		for bid, buffer in self.buffers.items():
			buffer_list.append( (bid, buffer.save_status, buffer.get_name()) )
		return buffer_list

	# checks to see if a backup file for a given filename exists
	# backup files start with a ".ash.b-" prefix and reside in the same directory as its
	# parent file
	@staticmethod
	def backup_exists(filename):
		if(os.path.isfile(os.path.dirname(filename) + "/.ash.b-" + get_file_title(filename))):
			return True
		else:
			return False

	# checks to see if a specified file is a text file
	@staticmethod
	def is_binary(filename):
		if(not os.path.isfile(filename)): return True
		mt = str(mimetypes.guess_type(filename, strict=False)[0]).lower()
		if(mt.startswith("text/")):
			return False
		elif(mt != "none"):
			return True
		else:
			pf = predict_file_encoding(filename)
			if(pf == None): return True
			if(str(pf).lower() not in SUPPORTED_ENCODINGS): return True
			return False