# ---------------------------------------------------------------------------------------------
#  Copyright (c) Akash Nag. All rights reserved.
#  Licensed under the MIT License. See LICENSE.md in the project root for license information.
# ---------------------------------------------------------------------------------------------

# This is the entry point of the application

import sys
import os

from ash.main import *

ash_dir = os.path.dirname(os.path.realpath(__file__))
app = AshEditorApp(ash_dir, sys.argv)
app.run()