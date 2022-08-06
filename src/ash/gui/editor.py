# ---------------------------------------------------------------------------------------------
#  Copyright (c) Akash Nag. All rights reserved.
#  Licensed under the MIT License. See LICENSE.md in the project root for license information.
# ---------------------------------------------------------------------------------------------

# This module implements the text-editor widget

from ash.gui import *
from ash.gui.editorKeyHandler import *
from ash.gui.editorUtility import *
from ash.gui.cursorPosition import *
from ash.gui.popupMenu import *
from ash.core.editHistory import *

import pyximport; pyximport.install(language_level=3)
from ash.core.screen import *

# This is the text editor class
class Editor(Widget):
	def __init__(self, parent, area):
		super().__init__(WIDGET_TYPE_EDITOR, True, True)
		
		# initialize parent window
		self.parent = parent
		self.screen = None
		self.slave_cursors = list()
		self.app = self._get_app_object()

		# initialize helper classes
		self.utility = EditorUtility(self)
		self.keyHandler = EditorKeyHandler(self)

		# set up the text and cursor data structures
		self.curpos = CursorPosition(0,0)
		
		# set accepted charset
		self.separators = "~`!@#$%^&*()-_=+\\|[{]};:\'\",<.>/? "
		self.charset = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789"
		self.charset += self.separators
		
		# set initial selection status
		self.selection_mode = False
		self.sel_start = CursorPosition(0,0)
		self.sel_end = CursorPosition(0,0)
		self.highlighted_text = None
		self.find_match_case = False
		self.find_whole_words = False
		self.find_regex = False
		self.find_mode = False
		
		# set default tab size
		self.reset_preferences()
		self.is_in_focus = False

		self.popup_menu = None

		# use dummy values
		self.selection_mode = False
		self.bid = -1
		self.buffer = None
		self.resize(area.y, area.x, area.height, area.width, True)
		
	def _get_app_object(self):
		temp_obj = self
		temp_app = None

		while(temp_app == None):
			try:
				temp_app = temp_obj.app
			except:
				try:
					temp_obj = temp_obj.parent
				except:
					temp_obj = temp_obj.manager

		return temp_app

	def hide_menu_bar(self):
		self.popup_menu = None

	def reset(self):
		self.selection_mode = False
		self.curpos.x = 0
		self.curpos.y = 0
		self.slave_cursors = list()
		self.recompute()

	def set_buffer(self, bid, buffer):
		self.bid = bid
		self.buffer = buffer
		self.buffer.attach_editor(self)
		if(self.screen != None): self.screen.update(self.parent, self.buffer)
		self.reset()

	def destroy(self):			# called by TopLevelWindow.close_active_editor()
		self.buffer.detach_editor(self)

	def reset_preferences(self):
		self.tab_size = self.app.settings_manager.get_setting("tab_width")
		self.word_wrap = self.app.settings_manager.get_setting("wrap_text")
		self.hard_wrap = self.app.settings_manager.get_setting("hard_wrap")
		self.should_stylize = self.app.settings_manager.get_setting("syntax_highlighting")
		self.auto_close = self.app.settings_manager.get_setting("auto_close_matching_pairs")
		self.show_line_numbers = self.app.settings_manager.get_setting("line_numbers")
		self.show_scrollbars = self.app.settings_manager.get_setting("scrollbars")
		if(self.screen != None): self.screen.toggle_line_numbers_and_scrollbars(self.show_line_numbers, self.show_scrollbars)
		self.reset()
		self.repaint()
	
	# resize editor
	def resize(self, y, x, height, width, forced=False):
		if(not forced and height == self.height and width == self.width): return

		self.y = y
		self.x = x
		self.height = height
		self.width = width		
		if(self.screen == None):
			self.screen = Screen(self.app.supports_colors, self.parent, self.buffer, self.height, self.width, self.show_line_numbers, self.show_scrollbars)
		else:
			self.screen.resize(self.height, self.width)
		self.reset()

	# when focus received
	def focus(self):
		curses.curs_set(False)
		self.is_in_focus = True
		self.repaint()

	# when focus lost
	def blur(self):
		self.is_in_focus = False
		self.repaint()

	# returns the current cursor position
	def get_cursor_position(self):
		return str(self.curpos)

	# when key-press detected
	def perform_action(self, ch):
		if(ch == -1): return None
		if(not self.is_in_focus): self.focus()

		edit_made = False

		if(KeyBindings.is_key(ch, "RIGHT_CLICK")):
			edit_made = self.on_right_click()
		elif(KeyBindings.is_key(ch, "DELETE_CHARACTER_LEFT")):
			edit_made = self.keyHandler.handle_backspace_key(ch)
		elif(KeyBindings.is_key(ch, "DELETE_CHARACTER_RIGHT")):
			edit_made = self.keyHandler.handle_delete_key(ch)
		elif(KeyBindings.is_key(ch, "MOVE_CURSOR_TO_LINE_START") or KeyBindings.is_key(ch, "MOVE_CURSOR_TO_LINE_END")):
			self.keyHandler.handle_home_end_keys(ch)
		elif(KeyBindings.is_key(ch, "SELECT_TILL_LINE_START") or KeyBindings.is_key(ch, "SELECT_TILL_LINE_END")):
			self.keyHandler.handle_shift_home_end_keys(ch)
		elif(KeyBindings.is_key(ch, "MOVE_CURSOR_TO_DOCUMENT_START") or KeyBindings.is_key(ch, "MOVE_CURSOR_TO_DOCUMENT_END")):
			self.keyHandler.handle_ctrl_home_end_keys(ch)
		elif(KeyBindings.is_key(ch, "MOVE_CURSOR_LEFT") or KeyBindings.is_key(ch, "MOVE_CURSOR_RIGHT") or KeyBindings.is_key(ch, "MOVE_CURSOR_UP") or KeyBindings.is_key(ch, "MOVE_CURSOR_DOWN")):
			self.keyHandler.handle_arrow_keys(ch)
		elif(KeyBindings.is_key(ch, "MOVE_TO_PREVIOUS_PAGE") or KeyBindings.is_key(ch, "MOVE_TO_NEXT_PAGE")):
			self.keyHandler.handle_page_navigation_keys(ch)
		elif(KeyBindings.is_key(ch, "SELECT_PAGE_ABOVE") or KeyBindings.is_key(ch, "SELECT_PAGE_BELOW")):
			self.keyHandler.handle_shift_page_navigation_keys(ch)
		elif(KeyBindings.is_key(ch, "SELECT_CHARACTER_LEFT") or KeyBindings.is_key(ch, "SELECT_CHARACTER_RIGHT") or KeyBindings.is_key(ch, "SELECT_LINE_ABOVE") or KeyBindings.is_key(ch, "SELECT_LINE_BELOW")):
			self.keyHandler.handle_shift_arrow_keys(ch)
		elif(KeyBindings.is_key(ch, "MOVE_CURSOR_TO_PREVIOUS_WORD") or KeyBindings.is_key(ch, "MOVE_CURSOR_TO_NEXT_WORD")):
			self.keyHandler.handle_ctrl_arrow_keys(ch)
		elif(KeyBindings.is_key(ch, "INSERT_TAB") or KeyBindings.is_key(ch, "DECREASE_INDENT")):
			edit_made = self.keyHandler.handle_tab_keys(ch)
		elif(KeyBindings.is_key(ch, "NEWLINE")):
			edit_made = self.keyHandler.handle_newline()
		elif(str(chr(ch)) in self.charset):
			edit_made = self.keyHandler.handle_printable_character(ch)
		else:
			edit_made = self.keyHandler.handle_keys(ch)
		
		if(edit_made): self.buffer.update(self.curpos, self)
		self.recompute(edit_made)
			
	# <---------------------------- Calls Screen.recompute ---------------------

	def recompute(self, forced=True):
		if(self.screen != None): self.screen.recompute(self.curpos, self.tab_size, self.word_wrap, self.hard_wrap, forced)

	# <------------------- Functions called from BufferManager --------------------->

	def notify_update(self):
		if(self.curpos.y >= len(self.buffer.lines) or self.curpos.x > len(self.buffer.lines[self.curpos.y])):
			self.curpos.x = 0
			self.curpos.y = 0			
		if(self.selection_mode):
			if(self.sel_start.y >= len(self.buffer.lines) or self.sel_start.x > len(self.buffer.lines[self.sel_start.y]) or self.sel_end.y >= len(self.buffer.lines) or self.sel_end.x > len(self.buffer.lines[self.sel_end.y])):
				self.selection_mode = False
		
		self.repaint()

	def notify_merge(self, new_bid, new_buffer):
		self.bid = new_bid
		self.buffer = new_buffer
		self.selection_mode = False
		if(self.curpos.y >= len(self.buffer.lines) or self.curpos.x > len(self.buffer.lines[self.curpos.y])):
			self.curpos.x = 0
			self.curpos.y = 0
		self.repaint()

	# <---------------------------- Repaint Operations ----------------------------->

	# the primary draw routine for the editor
	def repaint(self):
		if(self.height <= 0 or self.width <= 0): return
		if(self.curpos.x < 0 or self.curpos.y < 0): return
		if(self.buffer == None or self.screen == None): return
		
		if(self.selection_mode and not self.find_mode):
			start, end = self.screen.get_selection_endpoints(self.sel_start, self.sel_end)
			if(start.y == end.y):
				self.highlighted_text = self.utility.get_selected_text()
				self.find_match_case = False
				self.find_whole_words = False
				self.find_regex = False
			else:
				self.highlighted_text = None
		elif(not self.find_mode):
			self.highlighted_text = None

		if(self.selection_mode):
			sel_info = {
				"start": self.sel_start,
				"end": self.sel_end
			}
		else:
			sel_info = None

		highlight_info = {
			"text": self.highlighted_text,
			"match_case": self.find_match_case,
			"whole_words": self.find_whole_words,
			"is_regex": self.find_regex
		}
		
		self.screen.render(self.curpos, self.tab_size, self.word_wrap, self.hard_wrap, sel_info, highlight_info, self.is_in_focus, self.slave_cursors, self.should_stylize)
		self.screen.draw(self.y, self.x)
		
		
		
	# <-------------------------------------------------------------------------------------->

	# <---------------------------- Data and File I/O ----------------------------->

	# returns the selection length (for incorporating into status-bar)
	def get_selection_length_as_string(self):
		return self.utility.get_selection_length_as_string()

	# returns information about editor-state
	def get_info(self):
		return({
			"x": self.x,
			"y": self.y,
			"height": self.height,
			"width": self.width,
			"screen": self.screen,
			"bid": self.bid,
			"buffer": self.buffer,
			"selection_mode": self.selection_mode,
			"sel_start": self.sel_start,
			"sel_end": self.sel_end,
			"tab_size": self.tab_size,
			"word_wrap": self.word_wrap,
			"hard_wrap": self.hard_wrap,
			"find_mode": self.find_mode,
			"search_text": self.highlighted_text,
			"match_case": self.find_match_case,
			"whole_words": self.find_whole_words,
			"is_regex": self.find_regex
		})		

	# <--------------------- stub functions ---------------------->

	# delete the selected text
	def delete_selected_text(self):
		return self.utility.delete_selected_text()
	
	# returns the selected text
	def get_selected_text(self):
		return self.utility.get_selected_text()

	# increase indent of selected lines
	def shift_selection_right(self):
		return self.utility.shift_selection_right()

	# decrease indent of selected lines
	def shift_selection_left(self):
		return self.utility.shift_selection_left()	
	
	# returns the block of leading whitespaces on a given line 
	def get_leading_whitespaces(self, line_index):
		return self.utility.get_leading_whitespaces(line_index)

	# returns the block of leading whitespaces on a given rendered line
	def get_leading_whitespaces_rendered(self, line_index):
		return self.utility.get_leading_whitespaces_rendered(line_index)
		
	# returns the selection endpoints in the correct order
	def get_selection_endpoints(self):
		return self.utility.get_selection_endpoints()

	# get file size
	def get_file_size(self):
		return self.utility.get_file_size()

	# <---------------------------- Find/Replace operations --------------------------------->

	# highlights all instances
	def find_all(self, search_text, match_case, whole_words, regex):
		self.utility.find_all(search_text, match_case, whole_words, regex)
		self.repaint()

	# cancels the find mode
	def cancel_find(self):
		self.utility.cancel_find()
		self.repaint()

	# find next match
	def find_next(self, search_text, match_case, whole_words, regex):
		self.utility.find_next(search_text, match_case, whole_words, regex)
		self.repaint()
		
	# find previous match
	def find_previous(self, search_text, match_case, whole_words, regex):
		self.utility.find_previous(search_text, match_case, whole_words, regex)
		self.repaint()
		
	# replace next instance
	def replace_next(self, search_text, replace_text, match_case, whole_words, regex):
		self.utility.replace_next(search_text, replace_text, match_case, whole_words, regex)
		self.repaint()
		
	# replace all instances
	def replace_all(self, search_text, replace_text, match_case, whole_words, regex):
		self.utility.replace_all(search_text, replace_text, match_case, whole_words, regex)
		self.repaint()

	# <---------------------------- mouse handling functions ------------------------->

	def get_bounds(self):
		return (self.y, self.x, self.height, self.width)

	def get_relative_coords(self, y, x):
		return (y - self.y, x - self.x)

	def on_click(self, y, x):
		if(self.popup_menu != None): self.popup_menu.hide_menu_bar()
		curpos = self.screen.get_curpos_after_click(y, x, self.buffer.lines, self.width, self.tab_size, self.word_wrap, self.hard_wrap)
		if(curpos != None): self.curpos = copy.copy(curpos)
		self.repaint()

	def on_right_click(self, y = -1, x = -1):
		if(y >= 0 and x >= 0): self.on_click(y, x)
		
		visual_curpos = self.screen.translate_real_to_visual_curpos(self.curpos, self.buffer.lines, self.width, self.tab_size, self.word_wrap, self.hard_wrap)
		app_dh = self.parent.tab.manager.app.dialog_handler

		if(visual_curpos == None):
			y, x = self.y + (self.height // 2), self.x + (self.width // 2)
		else:
			y, x = visual_curpos.y + self.y + 1, visual_curpos.x + self.x + 1
		
		popup_menu_items = [
			("Undo", True, self.keyHandler.handle_undo),
			("Redo", True, self.keyHandler.handle_redo),
			("---", False, None),
			("Cut", self.selection_mode, self.keyHandler.handle_cut),
			("Copy", self.selection_mode, self.keyHandler.handle_copy),
			("Paste", True, self.keyHandler.handle_paste),
			("---", False, None),
			("Find...", True, app_dh.invoke_find),
			("Find & Replace...", True, app_dh.invoke_find_and_replace),
			("---", False, None),
			("Preferences...", True, app_dh.invoke_set_preferences)
		]
		
		self.popup_menu = PopupMenu(self, y, x, popup_menu_items, supports_colors=self.app.supports_colors)
		ret_code = self.popup_menu.show()
		self.repaint()

		# return code is True means edit was made
		if(ret_code): self.buffer.update(self.curpos, self)

		return ret_code
		