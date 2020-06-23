# ---------------------------------------------------------------------------------------------
#  Copyright (c) Akash Nag. All rights reserved.
#  Licensed under the MIT License. See LICENSE.md in the project root for license information.
# ---------------------------------------------------------------------------------------------

# This is the entry point of the application
# To test-run the editor:
#	ash/src $	python3 ash.py

import sys
from ash.main import *

app = AshEditorApp(sys.argv)
app.run()