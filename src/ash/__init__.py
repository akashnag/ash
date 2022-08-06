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
import subprocess
import platform

__version__			= "0.1.0-dev"
__build__			= "13"
__release_date__	= "Aug 06, 2022"

APP_COPYRIGHT_TEXT	= "© Copyright 2020-2022, Akash Nag. All rights reserved."
APP_LICENSE_TEXT	= "Licensed under the MIT License."
APP_WEBSITE_URL		= "https://akashnag.github.io/ash"
APP_GITHUB_URL		= "https://github.com/akashnag/ash"

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
if platform.system() == "Linux":
    APP_DATA_DIR			= os.path.join(os.path.expanduser("~"), ".config", "ash-editor")
else:
    APP_DATA_DIR			= os.path.join(os.path.expanduser("~"), ".ash-editor")
APP_PLUGINS_DIR			= os.path.join(APP_DATA_DIR, "plugins")
APP_KEYMAPS_DIR			= os.path.join(APP_DATA_DIR, "keymaps")
APP_THEMES_DIR			= os.path.join(APP_DATA_DIR, "themes")

PROJECT_SETTINGS_DIR_NAME = ".ash-editor"
PROJECT_SETTINGS_FILE_NAME = "settings.json"

TEMP_OUTPUT_FILE		= os.path.join(APP_DATA_DIR, "temp.output")
LOG_FILE 				= os.path.join(APP_DATA_DIR, "log.txt")
SESSION_FILE			= os.path.join(APP_DATA_DIR, "session.dat")
SETTINGS_FILE			= os.path.join(APP_DATA_DIR, "settings.json")
INSTALLED_THEMES_FILE 	= os.path.join(APP_DATA_DIR, "installed_themes.txt")
INSTALLED_KEYMAPS_FILE 	= os.path.join(APP_DATA_DIR, "installed_keymaps.txt")

DEFAULT_SHELL			= "bash"
DEFAULT_TERMINAL		= "xterm"
