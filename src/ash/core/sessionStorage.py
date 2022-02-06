# ---------------------------------------------------------------------------------------------
#  Copyright (c) Akash Nag. All rights reserved.
#  Licensed under the MIT License. See LICENSE.md in the project root for license information.
# ---------------------------------------------------------------------------------------------

# This module handles all session persistence operations

import os
import pickle
import ash
from ash.core.logger import *

MAX_RECENT_FILES_RECORD		= 100
MAX_RECENT_PROJECTS_RECORD	= 5

class ProjectEditorData:
	def __init__(self, filename, curpos):
		self.filename = filename
		self.curpos = curpos

	def __str__(self):
		return f"[ProjectEditorData] curpos: {str(self.curpos)} filename: {self.filename}"

class ProjectTabData:
	def __init__(self, split_info, editor_data):
		self.editor_data_list = list(editor_data)			# contains a list of ProjectEditorData objects
		self.split_info_list = list(split_info)				# contains a list of splits

	def __str__(self):
		x = "[ProjectTabData]\n\t\tsplit-info: "
		y = "\n\t\teditor-data-list: "
		for s in self.split_info_list:
			x += str(s) + ","
		for e in self.editor_data_list:
			y += str(e)
		return x+y

class ProjectBufferData:
	def __init__(self, filename, backup_edit_count, undo_edit_count, history, lwt):
		self.filename = filename
		self.backup_edit_count = backup_edit_count
		self.undo_edit_count = undo_edit_count
		self.history = history
		self.last_write_time = lwt

	def __str__(self):
		return f"[ProjectBufferData] filename: {self.filename} bec: {self.backup_edit_count} uec: {self.undo_edit_count}"

class ProjectData:
	def __init__(self, active_tab_index, tab_data, buffer_data):
		self.active_tab_index = active_tab_index
		self.tab_data_list = tab_data						# contains a list of ProjectTabData objects
		self.buffer_data_list = buffer_data					# contains a list of Buffer.get_persistent_data()

	def __str__(self):
		x = "[ProjectData]:\n\ttab-data-list: "
		y = "\n\tbuffer-data-list: "
		for t in self.tab_data_list:
			x += str(t)
		for b in self.buffer_data_list:
			y += str(b)
		return x+y

class SessionData:
	def __init__(self, recent = None, projects = None, project_map = None):
		self.version = ash.__version__ + ash.__build__
		self.recent_files_list = list() if recent == None else list(recent)					# contains a list of strings (file paths)
		self.projects_list = list() if projects == None else list(projects)					# contains a list of project paths
		self.project_data_map = dict() if project_map == None else dict(project_map)		# contains a list of ProjectData objects
		
class SessionStorage:
	def __init__(self, app, window_manager, buffers):
		self.app = app
		self.window_manager = window_manager
		self.buffer_manager = buffers
		sd = self._load_from_file()
		if(sd == None):
			self.session_data = SessionData()
		else:
			self.session_data = SessionData(sd.recent_files_list, sd.projects_list, sd.project_data_map)

	def get_recent_files_list(self):
		return self.session_data.recent_files_list
	
	def does_project_have_saved_session(self, project_dir):
		project_data = self.session_data.project_data_map.get(project_dir)
		return(False if project_data == None else True)

	def set_project_session(self, project_dir):
		project_data = self.session_data.project_data_map.get(project_dir)
		if(project_data == None): return
		self.buffer_manager.set_persistent_data(project_data.buffer_data_list)
		self.window_manager.set_persistent_data(project_data.active_tab_index, project_data.tab_data_list)

	def add_opened_file_to_record(self, filename):
		if(filename.endswith("/")): filename = filename[:-1]

		if(filename in self.session_data.recent_files_list):
			self.session_data.recent_files_list.remove(filename)
		self.session_data.recent_files_list.append(filename)

		while(len(self.session_data.recent_files_list) > MAX_RECENT_FILES_RECORD):
			self.session_data.recent_files_list.pop(0)

	def destroy(self):
		if(self.app.app_mode == ash.APP_MODE_PROJECT):
			# get the data
			active_tab_index, tab_data_list = self.window_manager.get_persistent_data(self.app.project_dir)
			buffer_data_list = self.buffer_manager.get_persistent_data(self.app.project_dir)
			self.session_data.project_data_map[self.app.project_dir] = ProjectData(active_tab_index, tab_data_list, buffer_data_list)

			# save to recent projects
			if(self.app.project_dir in self.session_data.projects_list):
				self.session_data.projects_list.remove(self.app.project_dir)
			self.session_data.projects_list.append(self.app.project_dir)

			# if record exceeds limit, remove old projects
			while(len(self.session_data.projects_list) > MAX_RECENT_PROJECTS_RECORD):
				proj_dir_name = self.session_data.projects_list.pop(0)
				del self.session_data.project_data_map[proj_dir_name]

		# write session data to file
		self._write_to_file()

	def _write_to_file(self):
		sfp = open(ash.SESSION_FILE, "wb")
		pickle.dump(self.session_data, sfp, pickle.HIGHEST_PROTOCOL)
		sfp.close()

	def _load_from_file(self):
		if(not os.path.isfile(ash.SESSION_FILE)): return None

		sfp = open(ash.SESSION_FILE, "rb")
		session_data = pickle.load(sfp)
		sfp.close()

		if(session_data.version != ash.__version__): return None
		return session_data