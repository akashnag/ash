# ---------------------------------------------------------------------------------------------
#  Copyright (c) Akash Nag. All rights reserved.
#  Licensed under the MIT License. See LICENSE.md in the project root for license information.
# ---------------------------------------------------------------------------------------------

# This module handles all logging functions for diagnostic purposes

import traceback
from ash import *
from datetime import datetime	

MAX_RECENT_RECORD		= 100

# creates the log file: must be called at startup
def log_init():
	logFile = open(LOG_FILE, "wt")
	logFile.write("ash " + APP_VERSION + "\n" + str(datetime.now()) + "\n")
	logFile.close()

# appends data to the log
def log(data, limit=7):
	logFile = open(LOG_FILE, "at")
	logFile.write(str(data) + "\n")
	# uncomment following line to allow stack recording:
	#traceback.print_stack(limit=limit, file=logFile)
	logFile.close()

def recent_files_init():
	global recent_files_list
	recent_files_init = list()

	if(not os.path.isfile(RECENT_FILES_RECORD)): return
	recentFilesFile = open(RECENT_FILES_RECORD, "rt")
	list_data = recentFilesFile.read().splitlines()
	recentFilesFile.close()	
	for filename in list_data:
		recent_files_list.append(filename)

def add_opened_file_to_record(filename):
	global recent_files_list

	if(filename.endswith("/")): filename = filename[:-1]

	if(filename not in recent_files_list):
		recent_files_list.append(filename)
	else:
		recent_files_list.remove(filename)
		recent_files_list.append(filename)

	while(len(recent_files_list) > MAX_RECENT_RECORD):
		recent_files_list.pop(0)

	recentFilesFile = open(RECENT_FILES_RECORD, "wt")
	for filename in recent_files_list:
		if(os.path.isfile(filename) or os.path.isdir(filename)):
			recentFilesFile.write(filename + "\n")
	recentFilesFile.close()