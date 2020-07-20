# ---------------------------------------------------------------------------------------------
#  Copyright (c) Akash Nag. All rights reserved.
#  Licensed under the MIT License. See LICENSE.md in the project root for license information.
# ---------------------------------------------------------------------------------------------

# This module handles all logging functions for diagnostic purposes

import traceback
import ash
import os
from datetime import datetime	

# creates the log file: must be called at startup
def log_init():
	logFile = open(ash.LOG_FILE, "wt")
	logFile.write("ash " + ash.__version__ + "\n" + str(datetime.now()) + "\n")
	logFile.close()

# appends data to the log
def log(data, limit=7):
	logFile = open(ash.LOG_FILE, "at")
	logFile.write(str(data) + "\n")
	# uncomment following line to allow stack recording:
	#traceback.print_stack(limit=limit, file=logFile)
	logFile.close()

def recent_files_init():
	recent_files_init = list()

	if(not os.path.isfile(ash.RECENT_FILES_RECORD)): return
	recentFilesFile = open(ash.RECENT_FILES_RECORD, "rt")
	list_data = recentFilesFile.read().splitlines()
	recentFilesFile.close()	
	for filename in list_data:
		ash.recent_files_list.append(filename)

def add_opened_file_to_record(filename):
	if(filename.endswith("/")): filename = filename[:-1]

	if(filename not in ash.recent_files_list):
		ash.recent_files_list.append(filename)
	else:
		ash.recent_files_list.remove(filename)
		ash.recent_files_list.append(filename)

	while(len(ash.recent_files_list) > ash.MAX_RECENT_RECORD):
		ash.recent_files_list.pop(0)

	recentFilesFile = open(ash.RECENT_FILES_RECORD, "wt")
	for filename in ash.recent_files_list:
		if(os.path.isfile(filename) or os.path.isdir(filename)):
			recentFilesFile.write(filename + "\n")
	recentFilesFile.close()