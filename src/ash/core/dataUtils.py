# ---------------------------------------------------------------------------------------------
#  Copyright (c) Akash Nag. All rights reserved.
#  Licensed under the MIT License. See LICENSE.md in the project root for license information.
# ---------------------------------------------------------------------------------------------

# This module handles all miscellaneous global file and buffer I/O operations

from ash.core import *
from ash.core.utils import *

# <--------------------- global variables ----------------------->
file_assoc = dict()

# <--------------------- functions ------------------------------>
def read_file_associations(app):
	global file_assoc
	
	f = open(app.ash_dir + "/config/languages.conf", "rt")
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

def get_file_directory(filename):
	pos = filename.rfind("/")
	if(pos <= 0):
		return ""
	else:
		return filename[0:pos]

def get_file_size(filename):
	if(filename == None): 
		return None
	else:
		bytes = os.stat(filename).st_size
		if(bytes < 1000): return str(bytes) + " bytes"
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