# ---------------------------------------------------------------------------------------------
#  Copyright (c) Akash Nag. All rights reserved.
#  Licensed under the MIT License. See LICENSE.md in the project root for license information.
# ---------------------------------------------------------------------------------------------

import curses
import os
import sys
import copy
import glob

APP_VERSION			= "0.1.0-dev"
UNSAVED_BULLET		= "\u2022"
TICK_MARK			= "\u2713"

APP_MODE_FILE		= 1		# if ash is invoked with zero or more file names
APP_MODE_PROJECT	= 2		# if ash is invoked with a single directory name