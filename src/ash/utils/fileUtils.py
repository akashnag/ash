# ---------------------------------------------------------------------------------------------
#  Copyright (c) Akash Nag. All rights reserved.
#  Licensed under the MIT License. See LICENSE.md in the project root for license information.
# ---------------------------------------------------------------------------------------------

# This module handles all file related functions

from ash.utils import *

def get_file_title(filename):
	pos = filename.rfind("/")
	return filename[pos+1:]

def get_file_directory(filename):
	pos = filename.rfind("/")
	return filename[0:pos]

def filter_child_directories(parent_dir, dir_list):
	filtered = list()
	n = len(parent_dir)
	for d in dir_list:
		if(d.startswith(parent_dir + "/")):
			sd = d[n+1:]
			if(sd.find("/") == -1): filtered.append(d)
	return filtered

def get_relative_file_title(project_dir, filename):
	if(filename == None): return ""
	pos = project_dir.rfind("/")
	if(pos == 0):
		return filename[pos:]
	else:
		return filename[pos+1:]

def get_relative_subdirectories(project_dir, filename):		# filename must be a file, not a directory
	relpath = filename[len(project_dir):]
	pos = relpath.rfind("/")
	core = relpath[1:pos+1]
	n = len(core)
	subdir_list = list()
	for i in range(n):
		if(core[i] == "/"): subdir_list.append(project_dir + "/" + core[0:i])
	return subdir_list

def get_copy_filename(filename):
	pos1 = filename.rfind("/")
	dir = filename[0:pos1+1]
	ft = filename[pos1+1:]
	pos2 = ft.rfind(".")
	if(pos2 < 0):
		return filename + "-copy"
	else:
		return dir + ft[0:pos2] + "-copy" + ft[pos2:]

def predict_file_encoding(filename, n = 20):
	with open(filename, "rb") as f:
		rawdata = b"".join([f.readline() for _ in range(n)])
	return chardet.detect(rawdata)["encoding"]

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

def get_textfile_mimetype(filename):
	mt = str(mimetypes.guess_type(filename, strict=False)[0]).lower()
	pos = mt.find("/")
	if(pos < 0):
		return "unknown"
	else:
		return mt[pos+1:]