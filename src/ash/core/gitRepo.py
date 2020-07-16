# ---------------------------------------------------------------------------------------------
#  Copyright (c) Akash Nag. All rights reserved.
#  Licensed under the MIT License. See LICENSE.md in the project root for license information.
# ---------------------------------------------------------------------------------------------

# This module implemets the Git-status like functionality

from ash.core import *
from ash.formatting.formatting import *
from ash.formatting.colors import *
from git import Repo

class GitRepo:
	def __init__(self, repo_dir):
		self.repo_dir = repo_dir
		try:
			self.repo = Repo(self.repo_dir)
			self.has_repo = True
			self.refresh()
		except:
			self.repo = None
			self.has_repo = False

	def refresh(self, retry_repo = False):
		if(not self.has_repo): 
			if(not retry_repo): 
				return
			else:
				try:
					self.repo = Repo(self.repo_dir)
					self.has_repo = True
				except:
					self.repo = None
					self.has_repo = False
					return

		self.hcommit = self.repo.head.commit
		self.tree = self.hcommit.tree		
		self.untracked_files = copy.copy(self.repo.untracked_files)

		self.status = dict()

		for status_type in [ 'A', 'D', 'R', 'M', 'T' ]:
			temp_list = list()
			for diff_obj in self.hcommit.diff(None).iter_change_type(status_type):
				temp_list.append(copy.copy(diff_obj.a_path))
			self.status[status_type] = temp_list

		self.file_count = 0
		self.tree_count = 0
		
		for item in self.tree.traverse():
			self.file_count += item.type == 'blob'
			self.tree_count += item.type == 'tree'

	def get_file_count(self):
		if(self.has_repo): 
			return self.file_count
		else:
			return None

	def get_directory_count(self):
		if(self.has_repo): 
			return self.tree_count
		else:
			return None

	def get_file_status(self, filename):
		if(not self.has_repo or not os.path.isfile(filename)): return None
		filename = get_relative_file_title2(self.repo_dir, filename)
		if(filename in self.untracked_files): return "U"
		for status_type in [ 'A', 'D', 'R', 'M', 'T' ]:
			if(filename in self.status[status_type]): return status_type
		return None

	def is_dirty(self):
		if(self.has_repo and self.repo.is_dirty()):
			return True
		else:
			return False

	def get_directory_status(self, dirname):
		if(self.is_directory_dirty(dirname)):
			return UNSAVED_BULLET
		else:
			return None

	def is_directory_dirty(self, dirname):
		if(not self.has_repo or not os.path.isdir(dirname)): return False
		for f in self.untracked_files:
			if(is_file_under_directory(dirname, self.get_full_path(f))):
				return True
		for status_type in [ 'A', 'D', 'R', 'M', 'T' ]:
			files_list = self.status[status_type]
			for f in files_list:
				if(is_file_under_directory(dirname, self.get_full_path(f))):
					return True
		return False

	def get_full_path(self, rel_path):
		return os.path.join(self.repo_dir, rel_path)

	@staticmethod
	def has_repo_in_dir(dir):
		try:
			repo = Repo(dir)
			return True
		except:
			return False

	@staticmethod
	def format_status_type(st):
		if(st == None):
			return ("", None)
		elif(st == UNSAVED_BULLET):
			return (st, gc("gitstatus-M"))
		else:
			return (get_circled_letter(st), gc("gitstatus-" + st))

	@staticmethod
	def get_active_branch_name(dir):
		try:
			repo = Repo(dir)
			return repo.active_branch.name
		except:
			return None