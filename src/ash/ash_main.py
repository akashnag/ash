# SPDX-License-Identifier: GPL-2.0-only
#
# /src/ash/ash_main.py
#
# Copyright (C) 2022-2022  Akash Nag

# This is the entry point of the application

import sys
import os

from ash.main import *

def run():
	ash_dir = os.path.dirname(os.path.realpath(__file__))
	app = AshEditorApp(ash_dir, sys.argv)
	app.run()
	
if __name__ == "__main__":
	run()