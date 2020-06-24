# ---------------------------------------------------------------------------------------------
#  Copyright (c) Akash Nag. All rights reserved.
#  Licensed under the MIT License. See LICENSE.md in the project root for license information.
# ---------------------------------------------------------------------------------------------

# This module handles all miscellaneous global file and buffer I/O operations

from ash.widgets.utils import *

# <--------------------- global variables ----------------------->
file_assoc = dict()

# <--------------------- functions ------------------------------>
def read_file_associations():
	global file_assoc
	
	f = open("config/languages.conf", "rt")
	assoc = f.read().splitlines()
	f.close()

	file_assoc = dict()
	for a in assoc:
		x = a.split(":=")
		file_assoc[x[0].strip()] = x[1].strip()

def get_file_type(filename):
	pos = filename.rfind(".")
	ext = filename[pos+1:].strip().lower()
	return file_assoc.get(ext)	

def get_file_title(filename):
	if(filename == None): return "Untitled"
	pos = filename.rfind("/")
	if(pos == -1):
		return filename
	else:
		return filename[pos+1:]

def get_file_size(filename):
	bytes = os.stat(filename).st_size
	if(bytes < 1000):
		return str(bytes) + " bytes"
	else:
		kb = bytes / 1024
		if(kb >= 1000):
			mb = kb / 1024
			if(mb >= 1000):
				gb = mb / 1024
				if(gb >= 1000):
					tb = gb / 1024
					if(tb >= 1000):
						pb = tb / 1024
						return str(round(pb,2)) + " PB"
					else:
						return str(round(tb,2)) + " KB"
				else:
					return str(round(gb,2)) + " GB"
			else:
				return str(round(mb,2)) + " MB"
		else:
			return str(round(kb,2)) + " KB"

def file_exists_in_buffer(file_list, filename):
	for f in file_list:
		if(f.filename == filename):
			return True
	return False

def get_file_buffer_index(file_list, filename):
	n = len(file_list)
	for i in range(n):
		if(file_list[i].filename == filename): return i
	return -1

def save_to_buffer(files, ed):
	if(files == None or ed == None): return
	filedata = ed.get_data()
	filename = filedata.filename
	if(filename != None):
		bi = get_file_buffer_index(files, filename)
		if(bi > -1): 
			files[bi] = filedata
		else:
			raise Exception("ERROR in save_to_buffer()")

def load_from_buffer(files, ed):
	if(files == None or ed == None): return
	filename = ed.filename
	if(filename != None):
		bi = get_file_buffer_index(files, filename)
		if(bi > -1): ed.set_data(files[bi])

def write_all_buffers_to_disk(files):
	for f in files:
		data = f.buffer
		textFile = open(f.filename, "wt")
		textFile.write(data)
		textFile.close()
		f.save_status = True

def write_buffer_to_disk(files, filename):
	bi = get_file_buffer_index(files, filename)
	if(bi == -1):
		raise Exception("ERROR in write_buffer_to_disk()")
	else:
		data = files[bi].buffer
		textFile = open(filename, "wt")
		textFile.write(data)
		textFile.close()
		files[bi].save_status = True

def load_buffer_from_disk(files, filename):
	bi = get_file_buffer_index(files, filename)
	if(bi == -1):
		raise Exception("ERROR in load_buffer_from_disk()")
	else:
		textFile = open(filename, "rt")
		text = textFile.read()
		textFile.close()

		files[bi].buffer = text
		files[bi].save_status = True
		return text


def get_number_of_unsaved_files(files_list):
	count = 0
	for f in files_list:
		if(not f.save_status): count += 1
	return count

def get_number_of_unsaved_buffers(main_window):
	n = len(main_window.editors)
	count = 0
	for i in range(n):
		if(main_window.editors[i] != None and main_window.editors[i].filename == None and not main_window.editors[i].save_status):
			count += 1
	return count

def get_first_free_editor_index(main_window):
	n = len(main_window.editors)
	for i in range(n):
		if(main_window.editors[i] == None): return i
	
	# no free editor, so check if any editor exists with no-file and no-data
	for i in range(n):
		ed = main_window.editors[i]
		if(ed != None and not ed.has_been_allotted_file and len(ed.__str__()) == 0): return i
	
	return -1

# <----------------------- MAIN CODE --------------------------->
read_file_associations()