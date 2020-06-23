# ---------------------------------------------------------------------------------------------
#  Copyright (c) Akash Nag. All rights reserved.
#  Licensed under the MIT License. See LICENSE.md in the project root for license information.
# ---------------------------------------------------------------------------------------------

# This module handles all miscellaneous global 
# file and buffer operations

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


# <----------------------- MAIN CODE --------------------------->
read_file_associations()