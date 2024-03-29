# SPDX-License-Identifier: GPL-2.0-only
#
# /src/ash/__init__.py
#
# Copyright (C) 2022-2022  Akash Nag

# This is imported by all modules, sets global parameters

import curses
import os
import sys
import copy
import glob
import subprocess
import platform

__version__			= "0.1.0-dev"
__build__			= "14"
__release_date__	= "Aug 10, 2022"

APP_COPYRIGHT_TEXT	= "© Copyright 2020-2022, Akash Nag. All rights reserved."
APP_LICENSE_TEXT	= "Licensed under the GPL-2.0 License."
APP_WEBSITE_URL		= "https://akashnag.github.io/ash"
APP_GITHUB_URL		= "https://github.com/akashnag/ash"

# list of supported encodings
SUPPORTED_ENCODINGS = sorted([ 
                            "utf-8", "utf-7", "utf-16", "utf-32", 
                            "latin-1", "tis-620"
                            "big5", "gb2312", "gb18030", "euc-tw", "hz-gb-2312", 
                            "iso-2022-cn", "euc-jp", "shift_jis", "iso-2022-jp",
                            "euc-kr", "iso-2022-kr", "koi8-r", "maccyrillic", "ibm855",
                            "ibm866", "iso-8859-5", "windows-1251", "iso-8859-2",
                            "windows-1250", "iso-8859-5", "iso-8859-1", "windows-1252",
                            "iso-8859-7", "iso-8859-8", "windows-1253", "windows-1255"                            
                        ])

APP_MODE_FILE		= 1		# if ash is invoked with zero or more file names
APP_MODE_PROJECT	= 2		# if ash is invoked with a single directory name

# dictionary of settings for global access
SETTINGS			= None

# minimum resolution required for ash
MIN_WIDTH			= 102
MIN_HEIGHT			= 22

# no. of milliseconds to sleep before checking for input (decreasing it will increase CPU usage; increasing it will reduce responsiveness)
SLEEP_MS            = 10

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
APP_LOCALES_DIR			= os.path.join(APP_DATA_DIR, "locales")
APP_SNIPPETS_DIR		= os.path.join(APP_DATA_DIR, "snippets")

PROJECT_SETTINGS_DIR_NAME  = ".ash-editor"
PROJECT_SETTINGS_FILE_NAME = "settings.json"

TEMP_OUTPUT_FILE		= os.path.join(APP_DATA_DIR, "temp.output")
LOG_FILE 				= os.path.join(APP_DATA_DIR, "log.txt")
SESSION_FILE			= os.path.join(APP_DATA_DIR, "session.dat")
SETTINGS_FILE			= os.path.join(APP_DATA_DIR, "settings.json")

DEFAULT_SHELL			= "bash"
DEFAULT_TERMINAL		= "xterm"

THEME_FILE_EXTENSION    = ".json"
KEYMAP_FILE_EXTENSION   = ".json"
LOCALE_FILE_EXTENSION   = ".json"
SNIPPET_FILE_EXTENSION  = ".snippets"