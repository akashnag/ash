# ---------------------------------------------------------------------------------------------
#  Copyright (c) Akash Nag. All rights reserved.
#  Licensed under the MIT License. See LICENSE.md in the project root for license information.
# ---------------------------------------------------------------------------------------------

# This module handles all logging functions

def log_init():
	logFile = open("log.txt", "wt")
	logFile.close()

def log(data):
	logFile = open("log.txt", "at")
	logFile.write(str(data) + "\n")
	logFile.close()