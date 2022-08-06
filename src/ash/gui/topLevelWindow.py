# ---------------------------------------------------------------------------------------------
#  Copyright (c) Akash Nag. All rights reserved.
#  Licensed under the MIT License. See LICENSE.md in the project root for license information.
# ---------------------------------------------------------------------------------------------

# This module implements a TopLevel window, which always spans the entire screen
# An instance of Ash should contain exactly 1 TopLevel window visible at any given time

from ash import *

from ash.gui import *
from ash.gui.windowManager import *
from ash.gui.statusbar import *
from ash.gui.window import *
from ash.gui.menuBar import *
from ash.gui.popupMenu import *
from ash.core.bufferManager import *
from ash.core.gitRepo import *

# <-------------------- class declaration --------------->
class TopLevelWindow(Window):
	def __init__(self, app, stdscr, title, handler_func):
		super().__init__(0, 0, 0, 0, title)
		self.app = app
		self.win = stdscr
		self.handler_func = handler_func
		self.app_name = self.app.get_app_name()		

		self.window_manager = WindowManager(self.app, self)
		self.init_menu_bar()

		self.status = None
		self.show_statusbar = False
		self.toggle_statusbar_visibility()

	def toggle_statusbar_visibility(self):
		self.show_statusbar = not self.show_statusbar
		if(not self.show_statusbar):
			self.status = None
			self.repaint()
		else:
			self.readjust()

	def update_status(self):
		if(self.status == None): return
		aed = self.window_manager.get_active_editor()

		tab_size = ""
		language = ""
		editor_state = "inactive"
		cursor_position = ""
		loc_count = ""
		file_size = ""
		unsaved_file_count = ""
		encoding = ""

		if(aed != None):
			lines, sloc = aed.buffer.get_loc()
			loc_count = str(lines) + " lines (" + str(sloc) + " sloc)"
			
			if(aed.buffer.filename != None):
				if(os.path.isfile(aed.buffer.filename)): file_size = aed.buffer.get_file_size()
				
				language = get_textfile_mimetype(aed.buffer.filename)
				
				if(aed.buffer.save_status):
					editor_state = "saved"
				else:
					editor_state = "modified"
			else:
				editor_state = "unsaved"
				language = "unknown"

			cursor_position = str(aed.get_cursor_position()) + aed.get_selection_length_as_string()
			encoding = aed.buffer.encoding
			tab_size = str(aed.tab_size)
		
		unsaved_file_count = str(self.app.buffers.get_unsaved_count()) + "*"
		
		if(self.app.app_mode == APP_MODE_PROJECT):
			if(GitRepo.has_repo_in_dir(self.app.project_dir)):
				editor_state = GitRepo.get_active_branch_name(self.app.project_dir)

		self.status.set(0, editor_state)
		self.status.set(1, language)
		self.status.set(2, encoding)
		self.status.set(3, loc_count)
		self.status.set(4, file_size)		
		self.status.set(5, unsaved_file_count)
		self.status.set(6, tab_size)
		self.status.set(7, cursor_position, "right")
				
		if(aed != None):
			self.set_title(self.app.get_app_title(aed))
		else:
			self.set_title(self.app.get_app_title())
	
	# shows the window and starts the event-loop
	def show(self, welcome_msg = None):
		curses.curs_set(False)
		self.win.keypad(True)
		self.win.timeout(0)
		self.repaint(welcome_msg)
		
		while(self.win != None):
			ch = self.win.getch()
			if(ch == -1): continue
			
			# send Ctrl/Fn keypresses to main handler first
			if(self.handler_func != None):
				ch = self.handler_func(ch)
				if(self.win == None): return

			if(ch == -1): continue
			
			if(KeyBindings.is_key(ch, "SHOW_MENU_BAR")):
				self.show_menu_bar()
			elif(KeyBindings.is_key(ch, "HIDE_MENU_BAR")):
				self.hide_menu_bar()
			elif(self.menu_bar_visible and (KeyBindings.is_key(ch, "LIST_MOVE_SELECTION_UP") or KeyBindings.is_key(ch, "LIST_MOVE_SELECTION_DOWN") or KeyBindings.is_key(ch, "LIST_MOVE_SELECTION_NEXT") or KeyBindings.is_key(ch, "LIST_MOVE_SELECTION_PREVIOUS") or KeyBindings.is_key(ch, "LIST_MAKE_SELECTION"))):
				self.menu_bar.perform_action(ch)
			elif(KeyBindings.is_mouse(ch)):
				btn, y, x = KeyBindings.get_mouse(ch)
				if(btn == MOUSE_CLICK and y == 0 and self.menu_bar == None):
					self.show_menu_bar()
				elif(btn == MOUSE_CLICK and self.menu_bar != None and y == self.menu_bar.y):
					self.menu_bar.mouse_click(btn, y, x)
				elif(btn == MOUSE_CLICK or btn == MOUSE_RIGHT_CLICK):
					ed_list = self.window_manager.get_editors_in_active_tab()
					for i, w in enumerate(ed_list):
						if(is_enclosed(y, x, w.get_bounds())):
							self.window_manager.set_as_active_editor(w)
							ry, rx = w.get_relative_coords(y,x)
							if(btn == MOUSE_CLICK):
								w.on_click(ry, rx)
							else:
								w.on_right_click(ry, rx)
							break
			else:
				aed = self.get_active_editor()
				if(aed != None):
					aed.focus()
					aed.perform_action(ch)
			
			self.repaint()
	
	# repaint background
	def repaint_background(self):
		self.win.addstr(0, 0, " " * self.width, gc("titlebar"))
		for i in range(1, self.height-1):
			self.win.addstr(i, 0, " " * self.width, gc("background"))
		self.win.addstr(self.height-1, 0, " " * (self.width - 1), gc("background"))

	# draws the window
	def repaint(self, error_msg = None, caller=None):
		curses.curs_set(False)
		if(self.win == None): return
		
		self.update_status()
		self.readjust()
		self.win.clear()
		self.repaint_background()

		if(error_msg == None):
			if(self.status != None): self.status.repaint(self.win, self.width-1, self.height-1, 0)
		else:
			if(len(error_msg) + 1 > self.width - 1): error_msg = error_msg[0:self.width-2]
			self.win.addstr(self.height-1, 0, (" " + error_msg).ljust(self.width-1), gc("messagebox-background") | (0 if self.app.supports_colors else curses.A_REVERSE))
		
		try:
			title_text = self.title + " - " + self.app_name
			if(self.menu_bar_visible):
				self.menu_bar.repaint(self.width)
				if(len(self.title) == 0):
					self.win.addstr(0, self.width - 1 - len(self.app_name), self.app_name, curses.A_BOLD | gc("menu-bar"))
				else:
					self.win.addstr(0, self.width - 1 - len(title_text), self.title + " - ", gc("menu-bar"))
					self.win.addstr(0, self.width - 1 - len(self.app_name), self.app_name, curses.A_BOLD | gc("menu-bar"))
			else:
				if(len(self.title) == 0):
					self.win.addstr(0, 0, self.app_name.center(self.width), curses.A_BOLD | gc("titlebar"))
				else:
					ts = (self.width - len(title_text)) // 2
					self.win.addstr(0, ts, self.title + " - ", gc("titlebar"))
					self.win.addstr(0, ts + len(self.title + " - "), self.app_name, curses.A_BOLD | gc("titlebar"))

			self.window_manager.repaint()
		except:
			raise
		
		self.win.refresh()

	# driver function
	def addstr(self, y, x, text, style):
		self.win.addstr(y, x, text, style)

	def bottom_up_readjust(self):				# called from WindowManager
		self.app.readjust()

	def readjust(self):							# called from AshEditorApp
		if( (not self.show_statusbar or self.status != None) and self.height == self.app.screen_height and self.width == self.app.screen_width): return
		self.height, self.width = self.app.screen_height, self.app.screen_width
		
		# status-bar sections: total=101+1 (min) = 102
		# *status (8), *file-type (11), encoding(7), sloc (20), file-size (10), 
		# *unsaved-file-count (4), *tab-size (1), cursor-position (6+1+6+3+8=24)
		#self.status = StatusBar(self, [ 10, 13, 9, 22, 12, 6, 3, -1 ])
		
		if(self.show_statusbar): 
			self.status = StatusBar(self, [ 0.099, 0.1287, 0.0891, 0.2178, 0.1188, 0.0594, 0.0297, -1 ], supports_colors=self.app.supports_colors)
		
		self.window_manager.readjust()

	def invoke_activate_editor(self, buffer_id, buffer, new_tab=False):
		aed = self.get_active_editor()
		if(new_tab or aed == None):
			self.add_tab_with_buffer(buffer_id, buffer)
		else:
			aed.set_buffer(buffer_id, buffer)
		self.repaint()

	def toggle_filename_visibility(self):
		self.window_manager.toggle_filename_visibility()
		self.repaint()

	# <------------------------------------- menu bar related functions ----------------------->

	def init_menu_bar(self):
		self.menu_bar_visible = False
		self.menu_bar = None

	def show_menu_bar(self):
		aed = self.get_active_editor()
		aedkh = None
		aed_buffer = None
		if(aed != None): 
			aedkh = aed.keyHandler
			aed_buffer = aed.buffer
		adh = self.app.dialog_handler
		self.menu_bar = MenuBar(self, self.win, 0, 0, supports_colors=self.app.supports_colors)
		has_editor = (True if aed != None else False)

		file_menu_items = [
			("New File...", True, adh.invoke_file_new),
			("Open File/Project...", True, adh.invoke_file_open),
			("---", True, None),
			("Save", has_editor, self.save_active_editor),
			("Save As...", has_editor, (adh.invoke_file_save_as, aed_buffer) if has_editor else None),
			("Save & Close", has_editor, self.save_and_close_active_editor),
			("Save All", True, adh.handle_save_all),
			("---", True, None),
			("Close All", True, self.close_all_tabs),
			("Exit", True, adh.handle_exit)
		]

		edit_menu_items = [
			("Undo", has_editor, (aedkh.handle_undo if has_editor else None)),
			("Redo", has_editor, (aedkh.handle_redo if has_editor else None)),
			("---", True, None),
			("Cut", has_editor and aed.selection_mode, (aedkh.handle_cut if has_editor else None)),
			("Copy", has_editor and aed.selection_mode, (aedkh.handle_copy if has_editor else None)),
			("Paste", has_editor, (aedkh.handle_paste if has_editor else None)),
			("---", True, None),
			("Select All", has_editor, (aedkh.handle_select_all if has_editor else None)),
			("Select Line", has_editor, (aedkh.handle_select_line if has_editor else None)),
			("---", True, None),
			("Find", has_editor, adh.invoke_find),
			("Find & Replace", has_editor, adh.invoke_find_and_replace),
			("Find in all files", True, adh.invoke_project_find),
			("Find & Replace in all files", True, adh.invoke_project_find_and_replace)
		]

		view_menu_items = [
			("Go to line...", has_editor, adh.invoke_go_to_line),
			("Command Palette...", True, adh.invoke_command_palette),
			("Preferences...", has_editor, adh.invoke_set_preferences),
			("Open tabs...", True, adh.invoke_show_active_tabs),
			("---", True, None),
			("Active Buffers/Files...", True, adh.invoke_list_active_files),
			("Recent Files...", True, adh.invoke_recent_files),
			("Project Explorer...", self.app.app_mode == APP_MODE_PROJECT, adh.invoke_project_explorer),
			("---", True, None),
			((TICK_MARK + " Status bar" if self.show_statusbar else "Status bar"), True, self.toggle_statusbar_visibility)
		]

		tools_menu_items = [
			("Theme Manager...", True, adh.invoke_theme_manager),
			("Key Mappings...", True, adh.invoke_key_mappings_manager),
			("---", True, None),
			("Project Settings", self.app.app_mode == APP_MODE_PROJECT, adh.invoke_project_settings),
			("Global Settings", True, adh.invoke_global_settings)
		]

		run_menu_items = [
			("Compile file", has_editor, self.compile_current_file),
			("Execute file", has_editor, self.execute_current_file),
			("---", True, None),
			("Build project", self.app.app_mode == APP_MODE_PROJECT, self.build_current_project),
			("Execute project", self.app.app_mode == APP_MODE_PROJECT, self.execute_current_project)
		]

		window_menu_items = [
			("New Tab", True, self.add_blank_tab),
			("---", True, None),
			("Close active tab", True, self.close_active_tab),
			("Close active editor", True, self.close_active_editor),
			("Close all but active editor", True, self.close_all_except_active_editor),
			("---", True, None),
			("Split Horizontally", True, self.split_horizontally),
			("Split Vertically", True, self.split_vertically),
			("Merge Horizontally", True, self.merge_horizontally),
			("Merge Vertically", True, self.merge_vertically),
			("---", True, None),
			("Switch to next editor", True, self.switch_to_next_editor),
			("Switch to previous editor", True, self.switch_to_previous_editor),
			("Switch to next tab", True, self.switch_to_next_tab),
			("Switch to previous tab", True, self.switch_to_previous_tab)
		]

		help_menu_items = [
			("Key Bindings", True, adh.invoke_help_key_bindings),
			("About...", True, adh.invoke_help_about)
		]

		mnuFile = PopupMenu(self, 1, 0, file_menu_items, width=25, is_dropdown=True, parent_menu=self.menu_bar, supports_colors=self.app.supports_colors)
		mnuEdit = PopupMenu(self, 1, 6, edit_menu_items, width = 35, is_dropdown=True, parent_menu=self.menu_bar, supports_colors=self.app.supports_colors)
		mnuView = PopupMenu(self, 1, 12, view_menu_items, width=28, is_dropdown=True, parent_menu=self.menu_bar, supports_colors=self.app.supports_colors)
		mnuTools = PopupMenu(self, 1, 18, tools_menu_items, width=25, is_dropdown=True, parent_menu=self.menu_bar, supports_colors=self.app.supports_colors)
		mnuRun = PopupMenu(self, 1, 25, run_menu_items, width = 20, is_dropdown=True, parent_menu=self.menu_bar, supports_colors=self.app.supports_colors)
		mnuWindow = PopupMenu(self, 1, 30, window_menu_items, width = 35, is_dropdown=True, parent_menu=self.menu_bar, supports_colors=self.app.supports_colors)
		mnuHelp = PopupMenu(self, 1, 38, help_menu_items, width=20, is_dropdown=True, parent_menu=self.menu_bar, supports_colors=self.app.supports_colors)

		# |FILE||EDIT||VIEW||TOOLS||RUN||WINDOW||HELP|
		# 01234567890123456789012345678901234567890123

		self.menu_bar.add_menu("File", mnuFile)
		self.menu_bar.add_menu("Edit", mnuEdit)
		self.menu_bar.add_menu("View", mnuView)
		self.menu_bar.add_menu("Tools", mnuTools)
		self.menu_bar.add_menu("Run", mnuRun)
		self.menu_bar.add_menu("Window", mnuWindow)
		self.menu_bar.add_menu("Help", mnuHelp)

		self.menu_bar_visible = True
		self.repaint()

	def hide_menu_bar(self):
		self.menu_bar_visible = False
		self.menu_bar = None
		self.repaint()

	# <------------------------ functions for IDE functionalities ------------------------------->

	def compile_current_file(self):
		aed = self.get_active_editor()
		if(aed == None):
			self.app.show_error("No active file to compile!")
			return
		
		filename = aed.buffer.filename
		pos2 = filename.rfind(".")
		pos1 = filename.rfind("/")
		
		if(pos2 < 0 or pos1 < 0 or pos1 > pos2):
			self.app.show_error("File type can not be determined!")
			return

		if(filename == None):
			self.app.show_error("File must be saved first before compiling!")
			return

		extension = filename[pos2:].lower()
		filetitle_sans_extension = filename[pos1+1:pos2]
		file_directory = filename[:pos1]
		
		compile_settings = self.app.settings_manager.get_setting("compile_file_command")
		if(compile_settings == None or extension not in compile_settings):
			self.app.show_error("Compiler for this file-type not set!")
			return

		compiler_command = compile_settings[extension].strip()
		if(len(compiler_command) == 0):
			self.app.show_error("Compiler for this file-type not set!")
			return

		compiler_command = compiler_command.replace("%d", f'"{file_directory}"')
		compiler_command = compiler_command.replace("%e", f'"{filetitle_sans_extension}"')
		compiler_command = compiler_command.replace("%f", f"'{filename}'")
		
		self.app.command_interpreter.execute_shell_command_in_terminal([compiler_command])


	def execute_current_file(self):
		aed = self.get_active_editor()
		if(aed == None):
			self.app.show_error("No active file to execute!")
			return
		
		filename = aed.buffer.filename
		pos2 = filename.rfind(".")
		pos1 = filename.rfind("/")
		
		if(pos2 < 0 or pos1 < 0 or pos1 > pos2):
			self.app.show_error("File type can not be determined!")
			return

		if(filename == None):
			self.app.show_error("File must be saved first before executing!")
			return

		extension = filename[pos2:].lower()
		filetitle_sans_extension = filename[pos1+1:pos2]
		file_directory = filename[:pos1]
		
		execute_settings = self.app.settings_manager.get_setting("execute_file_command")
		if(execute_settings == None or extension not in execute_settings):
			self.app.show_error("Execution command for this file-type not set!")
			return

		execution_command = execute_settings[extension].strip()
		if(len(execution_command) == 0):
			self.app.show_error("Execution command for this file-type not set!")
			return

		execution_command = execution_command.replace("%d", f'"{file_directory}"')
		execution_command = execution_command.replace("%e", f'"{filetitle_sans_extension}"')
		execution_command = execution_command.replace("%f", f"'{filename}'")
		
		self.app.command_interpreter.execute_shell_command_in_terminal([execution_command])


	def build_current_project(self):
		if(self.app.app_mode != APP_MODE_PROJECT):
			self.app.show_error("No project active!")
			return

		build_command = self.app.settings_manager.get_setting("build_project_command").strip()
		if(len(build_command) == 0):
			self.app.show_error("Build command not set for this project!")
			return

		build_command = build_command.replace("%d", f'"{self.app.project_dir}"')
		self.app.command_interpreter.execute_shell_command_in_terminal([build_command])

	def execute_current_project(self):
		if(self.app.app_mode != APP_MODE_PROJECT):
			self.app.show_error("No project active!")
			return

		execution_command = self.app.settings_manager.get_setting("execute_project_command").strip()
		if(len(execution_command) == 0):
			self.app.show_error("Execution command not set for this project!")
			return

		execution_command = execution_command.replace("%d", f'"{self.app.project_dir}"')
		self.app.command_interpreter.execute_shell_command_in_terminal([execution_command])

	# <------------------------------------ stub functions ------------------------------->

	def get_editor_count(self):
		return self.window_manager.get_editor_count()
	
	def close_active_editor(self):
		self.window_manager.close_active_editor()
		self.repaint()

	def close_all_except_active_editor(self):
		self.window_manager.close_all_except_active_editor()
		self.repaint()

	def add_blank_tab(self):
		self.window_manager.add_blank_tab()
		self.repaint()

	def add_tab_with_buffer(self, bid, buffer):
		self.window_manager.add_tab_with_buffer(bid, buffer)
		self.repaint()

	def remove_tab(self, tab_index):
		self.window_manager.remove_tab(tab_index)
		self.repaint()

	def close_active_tab(self):
		self.window_manager.close_active_tab()
		self.repaint()

	def get_tabs_info(self):
		return self.window_manager.get_tabs_info()

	def get_tab_count(self):
		return self.window_manager.get_tab_count()

	def close_all_tabs(self):
		n = self.get_tab_count()
		while(n > 0):
			self.close_active_tab()
			n -= 1

	def switch_to_tab(self, tab_index):
		self.window_manager.switch_to_tab(tab_index)
		self.repaint()

	def switch_to_next_tab(self):
		self.window_manager.switch_to_next_tab()
		self.repaint()

	def switch_to_previous_tab(self):
		self.window_manager.switch_to_previous_tab()
		self.repaint()

	def get_active_editor(self):
		return self.window_manager.get_active_editor()

	def switch_to_next_editor(self):
		self.window_manager.switch_to_next_editor()
		self.repaint()

	def switch_to_previous_editor(self):
		self.window_manager.switch_to_previous_editor()
		self.repaint()

	def split_horizontally(self, new_bid = None):
		self.window_manager.split_horizontally(new_bid)
		self.repaint()

	def split_vertically(self, new_bid = None):
		self.window_manager.split_vertically(new_bid)
		self.repaint()

	def merge_horizontally(self):
		self.window_manager.merge_horizontally()
		self.repaint()
	
	def merge_vertically(self):
		self.window_manager.merge_vertically()
		self.repaint()

	def get_active_tab(self):
		return self.window_manager.get_active_tab()

	def get_active_tab_index(self):
		return self.window_manager.get_active_tab_index()

	def reload_active_buffer_from_disk(self):
		self.window_manager.reload_active_buffer_from_disk()
		self.repaint()

	def save_and_close_active_editor(self):
		aed = self.window_manager.get_active_editor()
		if(aed != None): aed.keyHandler.save_and_close()

	def save_active_editor(self):
		aed = self.window_manager.get_active_editor()
		if(aed != None): aed.keyHandler.handle_save()

	def open_in_new_tab(self, filename, curpos, highlight_info = None):
		buffer = self.app.buffers.get_buffer_by_filename(filename)
		if(buffer == None):
			bid, buffer = self.app.buffers.create_new_buffer(filename, has_backup=BufferManager.backup_exists(filename))
		else:
			bid = buffer.id

		self.window_manager.add_tab_with_buffer(bid, buffer)
		aed = self.window_manager.get_active_editor()

		if(curpos != None): 	
			aed.curpos = copy.copy(curpos)

		if(highlight_info != None):
			search_text = highlight_info.get("search_text")
			match_case = highlight_info.get("match_case")
			whole_words = highlight_info.get("whole_words")
			is_regex = highlight_info.get("is_regex")
			aed.find_all(search_text, match_case, whole_words, is_regex)

		self.repaint()