# ---------------------------------------------------------------------------------------------
#  Copyright (c) Akash Nag. All rights reserved.
#  Licensed under the MIT License. See LICENSE.md in the project root for license information.
# ---------------------------------------------------------------------------------------------

# This module implements the Buffer Management Interface

from ash.core import *
from ash.core.ashException import *
from ash.core.logger import *
from ash.gui.cursorPosition import *
from ash.core.editHistory import *
from ash.core.sessionStorage import *
from ash.formatting.syntaxHighlighting import *
from ash.formatting.formatting import *

import time

LARGE_FILE_THRESHOLD	= 1024 * 1024		# large file if size > 1 MB
BACKUP_FREQUENCY_SIZE	= 16				# backup after every 16 edits
HISTORY_FREQUENCY_SIZE	= 8					# undo: every 8 edit operations

# Buffer class: encapsulates a single buffer/file
class Buffer:
	def __init__(self, manager, id, filename = None, encoding = None, has_backup = False):
		self.manager = manager
		self.id = id
		self.filename = normalized_path(filename)
		self.encoding = encoding
		self.editors = list()
		self.display_name = None

		self.backup_edit_count = 0
		self.undo_edit_count = 0
		self.last_curpos = CursorPosition(0,0)
		self.last_called = None

		self.last_read_time = None
		self.last_write_time = None
		self.last_backup_time = None
		
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
		if(self.encoding == None): self.encoding = self.manager.app.settings_manager.get_setting("default_encoding")

	# set the text encoding for the buffer
	def set_encoding(self, encoding):
		self.encoding = encoding

	# attach an editor to the list of editors mapped to this buffer
	def attach_editor(self, editor):
		if(editor not in self.editors): self.editors.append(editor)
		
	# remove an attached editor from the list of editors
	def detach_editor(self, editor):
		if(editor in self.editors): self.editors.remove(editor)

	# checks to see if an editor is attached to this buffer
	def is_editor_attached(self, editor):
		return (True if editor in self.editors else False)

	# returns True if this buffer has been allocated a file on disk
	def has_file(self):
		return (False if self.filename == None else True)

	def add_change(self, curpos):
		self.history.add_change(self.lines, curpos)
		self.undo_edit_count = 0
		self.last_curpos = curpos

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
		self.check_if_modified_externally()

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
		self.check_if_modified_externally()
	
	# check if the file has been modified externally or has been deleted
	def check_if_modified_externally(self):
		if(self.filename == None): return
		last_time = max([self.last_read_time, self.last_write_time])
		if(os.path.isfile(self.filename)):
			last_mod_time = BufferManager.get_last_modified(self.filename)
			if(last_mod_time > last_time):
				if(self.manager.app.ask_question("RELOAD FILE", "This file has been modified externally.\nDo you want to reload it?")):
					self.reload_from_disk()
				else:
					self.last_read_time = last_mod_time
		else:
			self.make_backup()
			if(self.manager.app.ask_question("FILE DELETED", "This file no longer exists on disk.\nDo you want to recreate it?")):
				# recreate the file
				self.write_to_disk(self.filename)
			else:
				# treat as unsaved buffer
				self.filename = None
				self.backup_file = None
				self.display_name = "untitled-" + str(self.id + 1)
				self.last_read_time = None
				self.last_write_time = None
				self.last_backup_time = None
				self.save_status = False
				for ed in self.editors:
					ed.notify_update()

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
			self.encoding = self.manager.app.settings_manager.get_setting("default_encoding")

		for ed in self.editors:
			ed.notify_update()
	
	# write out a copy
	def write_a_copy(self, filename, encoding = None):
		if(encoding == None): encoding = self.manager.app.settings_manager.get_setting("default_encoding")
		textFile = codecs.open(filename, "w", encoding)
		for line in self.lines:
			textFile.write(line + "\n")
		textFile.close()

	# writes out the buffer to a file on disk
	def write_to_disk(self, filename = None):
		if(self.filename == None and filename == None): raise(AshException("Error 1: buffer.write_to_disk()"))
		if(filename != None): self.filename = normalized_path(filename)		# update filename even if filename has changed
		
		self.formatter = SyntaxHighlighter(self.filename)
		self.display_name = None

		self.write_a_copy(self.filename, self.encoding)
		
		self.last_write_time = time.time()
		if(self.last_read_time == None): self.last_read_time = self.last_write_time

		self.save_status = True
		self.backup_file = os.path.dirname(self.filename) + "/.ash.b-" + get_file_title(self.filename)

		self.backup_edit_count = 0
		self.undo_edit_count = 0
		if(self.manager.app.app_mode != APP_MODE_PROJECT): 
			self.manager.app.session_storage.add_opened_file_to_record(self.filename)

		self.fire_special_file_on_save_triggers()
		return self.manager.merge_if_required(self.id)

	# checks to see if current file is any one of special files, if so trigger refresh
	def fire_special_file_on_save_triggers(self):
		if(self.filename == self.manager.app.settings_manager.get_current_settings_file()):
			self.manager.app.settings_manager.reload_settings()
			aed = self.manager.app.main_window.get_active_editor()
			if(aed != None): aed.reset_preferences()
			self.manager.app.main_window.repaint()
			if(aed != None): aed.repaint()

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

	def get_persistent_data(self):
		return ProjectBufferData(self.filename, self.backup_edit_count, self.undo_edit_count, self.history, max([self.last_read_time, self.last_write_time]))
		
	# <------------------- private functions ---------------------->

	# makes a backup of the data
	def make_backup(self):
		if(self.backup_file == None): return
		self.write_a_copy(self.backup_file, self.encoding)
		self.last_backup_time = time.time()

	# reads data from the assigned file on disk; optionally from a backup file instead
	def read_file_from_disk(self, read_from_backup = False):
		filename = (self.backup_file if read_from_backup else self.filename)

		if(self.manager.is_binary(filename)): raise(AshException("Error: buffer: attempting to read binary file"))

		if(not os.path.isfile(filename)):
			textFile = codecs.open(filename, "w", self.encoding)
			textFile.close()

		try:
			if(int(os.stat(filename).st_size) > LARGE_FILE_THRESHOLD):
				self.lines = self.manager.app.load_file(filename, self.encoding)
				if(self.lines == None): raise(AshFileReadAbortedException(filename))
			else:
				self.lines = list()
				textFile = codecs.open(filename, "r", self.encoding)
				data  = " "
				while(len(data) > 0):
					data = textFile.readline()
					self.lines.append(data[:-1])
				textFile.close()

			self.last_read_time = time.time()
			if(self.last_write_time == None): self.last_write_time = self.last_read_time
		except AshFileReadAbortedException as e:
			raise
		except:			
			raise(AshException("error reading file: " + filename))

		if(not read_from_backup): 
			self.backup_file = os.path.dirname(self.filename) + "/.ash.b-" + get_file_title(self.filename)
			self.save_status = True
		else:
			self.save_status = False

		self.backup_edit_count = 0
		self.undo_edit_count = 0
		
		if(not read_from_backup and self.manager.app.app_mode != APP_MODE_PROJECT): 
			self.manager.app.session_storage.add_opened_file_to_record(self.filename)
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

	def find_all(self, search_text, match_case, whole_words, is_regex):
		# return a list of tuples(line_index, pos)
		search_results = list()
		for line_index, line in enumerate(self.lines):
			lower_text = line.lower()
			lower_stext = search_text.lower()
			
			corpus = (line if match_case else lower_text)
			
			if(is_regex or match_case):
				search = search_text
			else:
				search = lower_stext

			pos = -1
			while(True):
				if(is_regex):
					pos = find_regex(corpus[pos+1:], search)
				elif(whole_words):
					pos = find_whole_word(corpus[pos+1:], search)
				else:
					pos = corpus.find(search, pos+1)

				if(pos >= 0):
					search_results.append( (line_index, pos) )
				else:
					break
		return search_results

	def replace_all(self, search_result, length, replace_text):
		count = 0
		for result in search_result:
			line_index = result[0]
			pos = result[1]
			data = self.lines[line_index]
			self.lines[line_index] = data[0:pos] + replace_text + data[pos+length:]
			self.save_status = False
			count += 1
		self.major_update(self.last_curpos, None, True)
		return count

# Buffer Manager class: for keeping track of the list of all active buffers
class BufferManager:
	def __init__(self, app):
		self.app = app
		self.buffers = dict()
		self.buffer_count = 0
	
	# creates a new buffer: either blank or from a file on disk
	def create_new_buffer(self, filename = None, encoding = None, has_backup = False):
		if(self.does_file_have_its_own_buffer(filename)): raise(AshException("Error 5: buffermanager.create_new_buffer()"))
		if(encoding == None):
			if(filename == None or not os.path.isfile(filename)):
				encoding = self.app.settings_manager.get_setting("default_encoding")
			else:
				encoding = predict_file_encoding(filename)
		try:
			self.buffers[self.buffer_count] = Buffer(self, self.buffer_count, filename, encoding, has_backup)
			self.buffer_count += 1
			return (self.buffer_count - 1, self.buffers[self.buffer_count - 1])
		except AshFileReadAbortedException as e:
			self.buffers[self.buffer_count] = None
			return (None, None)

	# creates a new buffer: either blank or from a file on disk
	def create_new_buffer_from_data(self, data):
		self.buffers[self.buffer_count] = Buffer(self, self.buffer_count, None, self.app.settings_manager.get_setting("default_encoding"), False)
		self.buffers[self.buffer_count].render_data_to_lines(data)
		self.buffer_count += 1
		return (self.buffer_count - 1, self.buffers[self.buffer_count - 1])

	# map an editor to a buffer specified by its buffer ID
	def attach_editor(self, buffer_id, editor):
		if(buffer_id >= self.buffer_count):
			raise(AshException("Error 2: buffermanager.attach_editor()"))
		else:
			self.buffers[buffer_id].attach_editor(editor)

	# removes an editor-mapping from a buffer specified by its buffer ID
	def detach_editor(self, buffer_id, editor):
		if(buffer_id >= self.buffer_count):
			raise(AshException("Error 3: buffermanager.detach_editor()"))
		else:
			self.buffers[buffer_id].detach_editor(editor)

	# returns the number of buffers currently active
	def __len__(self):
		return self.buffer_count

	# returns the display name of the specified buffer
	def get_name(self, buffer_id):
		if(buffer_id >= self.buffer_count):
			raise(AshException("Error 6: buffermanager.get_name()"))
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
		return self.write_all(True)
						
	# writes all buffers to disk
	def write_all(self, ignore_errors=False):
		counter=0
		for bid, buffer in self.buffers.items():
			if(not buffer.save_status):
				if(buffer.filename == None):
					counter += 1
					if(not ignore_errors): 
						raise(AshException("Error 4.1: buffermanager.write_all()"))
				else:
					try:
						buffer.write_to_disk()
					except:
						if(not ignore_errors): raise(AshException("Error 4.2: buffermanager.write_all()"))
		return counter

	# destroy all buffers, reset counter
	def destroy(self):
		for bid, buffer in self.buffers.items():
			buffer.destroy()

		self.buffer_count = 0
		self.buffers = dict()

	# destroy a specific buffer
	def destroy_buffer(self, bid):
		if(bid in self.buffers):
			del self.buffers[bid]
			self.buffer_count -= 1

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

	def find_all(self, search_text, match_case, whole_words, is_regex):
		search_results = dict()
		for bid, buffer in self.buffers.items():
			search_results[bid] = buffer.find_all(search_text, match_case, whole_words, is_regex)
		return search_results

	def replace_all(self, search_text, replace_text, match_case, whole_words, is_regex):
		search_results = self.find_all(search_text, search_text, match_case, whole_words, is_regex)
		count = 0
		buffer_count = 0
		for bid, buffer in self.buffers.items():
			info = search_results.get(bid)
			if(info != None): 
				x = buffer.replace_all(info, len(search_text), replace_text)
				count += x
				if(x > 0): buffer_count += 1
		return(count, buffer_count)

	def get_persistent_data(self, project_dir):
		pdata = list()
		for bid, buffer in self.buffers.items():
			if(buffer.filename != None and buffer.filename.startswith(project_dir + "/")):
				pdata.append(buffer.get_persistent_data())
		return pdata

	def set_persistent_data(self, buffer_data_list):
		for buffer_data in buffer_data_list:
			filename = buffer_data.filename
			buffer = self.get_buffer_by_filename(filename)

			last_mod_time = BufferManager.get_last_modified(filename)
			if(last_mod_time > buffer_data.last_write_time): continue			# ignore undo history since file modified externally

			buffer.backup_edit_count = buffer_data.backup_edit_count
			buffer.undo_edit_count = buffer_data.undo_edit_count
			buffer.history = buffer_data.history

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
		elif(mt in ["application/json", "application/xml", "application/xhtml+xml"]):
			return False
		elif(mt != "none"):
			return True
		else:
			pf = predict_file_encoding(filename)
			if(pf == None): return True
			if(str(pf).lower() not in SUPPORTED_ENCODINGS): return True
			return False

	# find the modified time of a file
	@staticmethod
	def get_last_modified(filename):
		return os.path.getmtime(filename)