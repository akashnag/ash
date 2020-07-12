# ---------------------------------------------------------------------------------------------
#  Copyright (c) Akash Nag. All rights reserved.
#  Licensed under the MIT License. See LICENSE.md in the project root for license information.
# ---------------------------------------------------------------------------------------------

# This module handles all logging functions for diagnostic purposes

from ash import *
from datetime import datetime	

# creates the log file: must be called at startup
def log_init():
	logFile = open(LOG_FILE, "wt")
	logFile.write(str(datetime.now()) + "\n")
	logFile.close()

# appends data to the log
def log(data):
	logFile = open(LOG_FILE, "at")
	logFile.write(str(data) + "\n")
	logFile.close()