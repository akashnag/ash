# ---------------------------------------------------------------------------------------------
#  Copyright (c) Akash Nag. All rights reserved.
#  Licensed under the MIT License. See LICENSE.md in the project root for license information.
# ---------------------------------------------------------------------------------------------

# This module handles all file related functions

import ash
from ash.utils import *
from ash.utils.utils import *

def normalized_path(path):
	if(path == None): return None
	return os.path.abspath(os.path.expanduser(path))

# returns the name of the file without its directory
def get_file_title(filename):
	pos = filename.rfind("/")
	return filename[pos+1:]

# returns a list of directories in dir_list which are under parent_dir
def filter_child_directories(parent_dir, dir_list):
	filtered = list()
	n = len(parent_dir)
	for d in dir_list:
		if(d.startswith(parent_dir + "/")):
			sd = d[n+1:]
			if(sd.find("/") == -1): filtered.append(d)
	return filtered

# get the file name of a file with respect to project_dir (keeps the project_dir name)
def get_relative_file_title(project_dir, filename):
	if(filename == None): return ""
	if(not filename.startswith(project_dir)): return filename
	pos = project_dir.rfind("/")
	if(pos == 0):
		return filename[pos:]
	else:
		return filename[pos+1:]

# get the file name of a file with respect to project_dir (removes the project_dir name)
def get_relative_file_title2(project_dir, filename):
	if(filename == None): return ""
	if(not filename.startswith(project_dir)): return filename
	if(project_dir == "/"):
		return filename[1:]
	else:
		return filename[len(project_dir)+1:]

# get all sub-directories w.r.t. filename and project_dir
def get_relative_subdirectories(project_dir, filename):		# filename must be a file, not a directory
	relpath = filename[len(project_dir):]
	pos = relpath.rfind("/")
	core = relpath[1:pos+1]
	n = len(core)
	subdir_list = list()
	for i in range(n):
		if(core[i] == "/"): subdir_list.append(project_dir + "/" + core[0:i])
	return subdir_list

def is_file_under_directory(dirname, filename):
	return(True if filename.startswith(dirname + "/") else False)

# returns a new filename from an existing filename to serve as a copy during Save As...
def get_copy_filename(filename):
	pos1 = filename.rfind("/")
	dir = filename[0:pos1+1]
	ft = filename[pos1+1:]
	pos2 = ft.rfind(".")
	if(pos2 < 0):
		return filename + "-copy"
	else:
		return dir + ft[0:pos2] + "-copy" + ft[pos2:]

# predict the encoding of a file
def predict_file_encoding(filename, n = 20):
	if(not os.path.isfile(filename)): return None
	fs = int(os.stat(filename).st_size)
	n = min([fs, n])
	with open(filename, "rb") as f:
		rawdata = b"".join([f.readline() for _ in range(n)])
	enc = chardet.detect(rawdata)["encoding"]
	return ("utf-8" if enc == "ascii" else enc)		# assume UTF-8

# returns the size of a filename formatted in units
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

# get the mime-type of a file
def get_textfile_mimetype(filename):
	mt = str(mimetypes.guess_type(filename, strict=False)[0]).lower()
	pos = mt.find("/")
	if(pos < 0):
		return "unknown"
	else:
		return mt[pos+1:]

# checks if a file rests in any of the IGNORED DIRECTORIES or has an extension in IGNORED_FILE_EXTENSIONS
def should_ignore_file(filename):
	IGNORED_FILE_EXTENSIONS = ash.SETTINGS.get("ignored_file_extensions")
	IGNORED_DIRECTORIES = ash.SETTINGS.get("ignored_directories")

	pos = filename.rfind(".")
	if(os.path.isfile(filename) and pos > -1):		
		ext = filename[pos:]
		if(ext in IGNORED_FILE_EXTENSIONS): return True

	positions = get_delim_positions(filename[1:], "/")
	last_pos = -1
	for pos in positions:
		dir = filename[last_pos+1:pos]
		last_pos = pos
		if(dir in IGNORED_DIRECTORIES): return True
	return False

# check if a directory is in any of the IGNORED DIRECTORIES
def should_ignore_directory(dirname):
	if(get_file_title(dirname) not in ash.SETTINGS.get("ignored_directories")):
		return False
	else:
		return True