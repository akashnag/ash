# ---------------------------------------------------------------------------------------------
#  Copyright (c) Akash Nag. All rights reserved.
#  Licensed under the MIT License. See LICENSE.md in the project root for license information.
# ---------------------------------------------------------------------------------------------

# This is imported by all modules, sets global parameters

import curses
import os
import sys
import copy
import glob

__version__			= "0.1.0-dev"
__revision__		= "7.0"
__release_date__	= "Dec 22, 2020"

APP_COPYRIGHT_TEXT	= "© Copyright 2020, Akash Nag. All rights reserved."
APP_LICENSE_TEXT	= "Licensed under the MIT License."

UNSAVED_BULLET		= "\u2022"
TICK_MARK			= "\u2713"

# list of supported encodings
SUPPORTED_ENCODINGS = [ "utf-8", "ascii", "utf-7", "utf-16", "utf-32", "latin-1" ]

APP_MODE_FILE		= 1		# if ash is invoked with zero or more file names
APP_MODE_PROJECT	= 2		# if ash is invoked with a single directory name

# dictionary of settings for global access
SETTINGS			= None

# minimum resolution required for ash
MIN_WIDTH			= 102
MIN_HEIGHT			= 22

# minimum dimensions for any particular editor
MIN_EDITOR_WIDTH	= 15
MIN_EDITOR_HEIGHT	= 5

# path to the application data directory and configuration files
APP_DATA_DIR			= os.path.join(os.getenv("HOME"), ".ash-editor")
APP_PLUGINS_DIR			= os.path.join(APP_DATA_DIR, "plugins")
APP_KEYMAPS_DIR			= os.path.join(APP_DATA_DIR, "keymaps")
APP_THEMES_DIR			= os.path.join(APP_DATA_DIR, "themes")

LOG_FILE 				= os.path.join(APP_DATA_DIR, "log.txt")
SESSION_FILE			= os.path.join(APP_DATA_DIR, "session.dat")
SETTINGS_FILE			= os.path.join(APP_DATA_DIR, "settings.dat")
INSTALLED_THEMES_FILE 	= os.path.join(APP_DATA_DIR, "installed_themes.txt")
INSTALLED_KEYMAPS_FILE 	= os.path.join(APP_DATA_DIR, "installed_keymaps.txt")