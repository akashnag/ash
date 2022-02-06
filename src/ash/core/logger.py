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
def log_init(preserve = False):
	logFile = open(ash.LOG_FILE, ("at" if preserve else "wt"))
	logFile.write("ash " + ash.__version__ + ash.__build__ + "\n" + str(datetime.now()) + "\n")
	logFile.close()

# appends data to the log
def log(data):
	logFile = open(ash.LOG_FILE, "at")
	logFile.write(str(data) + "\n")
	logFile.close()

# appends error to log
def log_error(error_msg, limit=7):
	logFile = open(ash.LOG_FILE, "at")
	logFile.write("ERROR: " + str(error_msg) + "\n")
	traceback.print_stack(limit=limit, file=logFile)
	logFile.close()