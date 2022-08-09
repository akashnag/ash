# ---------------------------------------------------------------------------------------------
#  Copyright (c) Akash Nag. All rights reserved.
#  Licensed under the MIT License. See LICENSE.md in the project root for license information.
# ---------------------------------------------------------------------------------------------

# This module handles snippets

import ash
import os
from ash.utils.utils import *

class SnippetManager:
	def __init__(self, app):
		self.app = app
		if(not os.path.isdir(ash.APP_SNIPPETS_DIR)): os.mkdir(ash.APP_SNIPPETS_DIR)
		
	def get_snippets(self, file_extension):
		filename = os.path.join(ash.APP_SNIPPETS_DIR, file_extension + ash.SNIPPET_FILE_EXTENSION)
		if(os.path.isfile(filename)):
			return self.read_snippet_file(filename)
		else:
			return dict()

	def get_snippet(self, name, file_extension):
		data = self.get_snippets(file_extension)
		if(name in data): return data[name]
		return None

	def read_snippet_file(self, filename):
		snippets = dict()
		current_data = []
		current_snippet_name = None

		file = open(filename, "rt")
		for line in file:
			line = line.replace("\n", "").replace("\r", "")
			start_flag = line.startswith("snippet ")
			end_flag = (line == "endsnippet")
			
			if(current_snippet_name == None and start_flag):
				current_snippet_name = line[8:].strip()
				if(current_snippet_name[0].isdigit()):
					log(f"ERROR in reading snippet file: {filename}, snippet name must not start with digit.")
					file.close()
					return dict()
			elif(current_snippet_name != None):
				if(end_flag):
					snippets[current_snippet_name] = "\n".join(current_data)
					current_data = []
					current_snippet_name = None
				else:
					current_data.append(line)
		file.close()
		
		return snippets
