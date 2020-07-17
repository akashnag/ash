# ---------------------------------------------------------------------------------------------
#  Copyright (c) Akash Nag. All rights reserved.
#  Licensed under the MIT License. See LICENSE.md in the project root for license information.
# ---------------------------------------------------------------------------------------------

# This is a helper module to assist with various dialogs

from ash import *
from ash.gui import *

from ash.core.bufferManager import *
from ash.gui.modalDialog import *
from ash.gui.findReplaceDialog import *
from ash.gui.checkbox import *
from ash.gui.listbox import *
from ash.gui.textfield import *
from ash.gui.treeview import TreeView

class DialogHandler:
	def __init__(self, app):
		self.app = app

	# <----------------------------------- Find and Replace --------------------------------->

	def invoke_find(self):
		mw = self.app.main_window
		ed = mw.get_active_editor()
		self.app.readjust()

		try:
			y, x = get_center_coords(self.app, 5, 30)
		except:
			self.app.warn_insufficient_screen_space()			
			return

		self.app.dlgFind = FindReplaceDialog(mw, y, x, ed)
		self.app.dlgFind.show()
		mw.repaint()

	def invoke_find_and_replace(self):
		mw = self.app.main_window
		ed = mw.get_active_editor()
		self.app.readjust()

		try:
			y, x = get_center_coords(self.app, 7, 30)
		except:
			self.app.warn_insufficient_screen_space()
			return

		self.app.dlgReplace = FindReplaceDialog(mw, y, x, ed, True)
		self.app.dlgReplace.show()
		mw.repaint()

	# <----------------------------------- Go to Line --------------------------------->

	def invoke_go_to_line(self):
		self.app.readjust()
		
		try:
			y, x = get_center_coords(self.app, 5, 14)
		except:
			self.app.warn_insufficient_screen_space()
			return

		self.app.dlgGoTo = ModalDialog(self.app.main_window, y, x, 5, 14, "GO TO LINE", self.go_to_key_handler)
		currentLine = str(self.app.main_window.get_active_editor().curpos.y + 1)
		txtLineNumber = TextField(self.app.dlgGoTo, 3, 2, 10, currentLine, True, callback = self.go_to_live_preview_key_handler)
		self.app.dlgGoTo.add_widget("txtLineNumber", txtLineNumber)
		self.app.old_goto_curpos = copy.copy(self.app.main_window.get_active_editor().curpos)
		self.app.dlgGoTo.show()

	def go_to_key_handler(self, ch):
		if(is_ctrl(ch, "Q")):
			self.app.main_window.get_active_editor().curpos = copy.copy(self.app.old_goto_curpos)
			self.app.dlgGoTo.hide()
			self.app.main_window.repaint()
		return ch

	def go_to_live_preview_key_handler(self, ch):
		if(is_newline(ch) or str(chr(ch)) in ".0123456789"):
			isn = is_newline(ch)
			line = str(self.app.dlgGoTo.get_widget("txtLineNumber"))
			
			if(len(line) == 0):
				if(isn): 
					beep()
					return -1

			pos = line.find(".")
			try:
				if(pos > -1):
					row = int(line[0:pos]) - 1
					col = int(line[pos+1:]) - 1
				else:
					row = int(line) - 1
					col = 0
			except:
				if(isn): 
					self.app.show_error("Invalid line number specified")
					return -1
				else:
					return ch
			
			aed = self.app.main_window.get_active_editor()
			if(row < 0 or row >= len(aed.buffer.lines)):
				beep()
			elif(col < 0 or col > len(aed.buffer.lines[row])):
				beep()
			else:
				if(isn): self.app.dlgGoTo.hide()
				aed.curpos.y = row
				aed.curpos.x = col
				self.app.main_window.repaint()				
		
		return ch

	# <----------------------------------- Close Editor/App --------------------------------->

	def invoke_forced_quit(self):
		self.app.main_window.hide()

	def invoke_quit(self):
		mw = self.app.main_window
		aed = mw.get_active_editor()
		am = self.app.app_mode

		unsaved_count = self.app.buffers.get_true_unsaved_count()
		editor_count = mw.get_editor_count()
		
		if(unsaved_count == 0):
			if(editor_count <= 1 and am == APP_MODE_FILE):
				mw.hide()
			elif(editor_count == 0 and am == APP_MODE_PROJECT):
				mw.hide()
			else:
				mw.close_active_editor()
		else:
			if(aed != None): 
				mw.close_active_editor()
				return
			
			response = self.app.ask_question("SAVE/DISCARD ALL", "One or more unsaved files exist, choose:\nYes: save all filed-changes and quit\nNo: discard all unsaved changes and quit\nCancel: don't quit", True)
			if(response == None): return
			if(response): self.app.buffers.write_all_wherever_possible()
			
			mw.hide()
			
	# <--------------------------- Recent Files List ------------------------------>

	def invoke_recent_files(self):
		self.app.readjust()

		if(len(recent_files_list) == 0):
			self.app.show_error("No recent files on record")
			return

		try:
			y, x = get_center_coords(self.app, 20, 80)
		except:
			self.app.warn_insufficient_screen_space()
			return

		self.app.dlgRecentFiles = ModalDialog(self.app.main_window, y, x, 20, 80, "RECENT FILES", self.recent_files_key_handler)
		lstRecentFiles = ListBox(self.app.dlgRecentFiles, 3, 2, 76, 16)
		
		for i in range(len(recent_files_list)-1, -1, -1):
			if(os.path.isfile(recent_files_list[i])):
				disp = get_file_title(recent_files_list[i]) + " [" + os.path.dirname(recent_files_list[i]) + "/]"
				lstRecentFiles.add_item(disp, tag=recent_files_list[i])

		self.app.dlgRecentFiles.add_widget("lstRecentFiles", lstRecentFiles)
		self.app.dlgRecentFiles.show()

	def recent_files_key_handler(self, ch):
		if(is_ctrl(ch, "Q") or is_func(ch, 12)):
			self.app.dlgRecentFiles.hide()
			self.app.main_window.repaint()
			return -1
		elif(is_newline(ch)):
			mw = self.app.main_window

			index = self.app.dlgRecentFiles.get_widget("lstRecentFiles").get_sel_index()
			filename = recent_files_list[len(recent_files_list) - 1 - index]
			self.app.dlgRecentFiles.hide()
			mw.repaint()
			
			if(not os.path.isfile(filename)):
				self.app.show_error("The selected file does not exist")
				return -1

			if(BufferManager.is_binary(filename)):
				self.app.show_error("Cannot open binary file!")
				mw.repaint()
				self.app.dlgRecentFiles.repaint()
				return -1

			sel_buffer = self.app.buffers.get_buffer_by_filename(filename)
			if(sel_buffer == None):
				sel_bid, sel_buffer = self.app.buffers.create_new_buffer(filename=filename, has_backup=BufferManager.backup_exists(filename))
			
			self.app.dlgRecentFiles.hide()

			mw.invoke_activate_editor(sel_buffer.id, sel_buffer)
			return -1
			
		return ch
	
	# <--------------------------- Set Preferences ------------------------------>

	def invoke_set_preferences(self):
		aed = self.app.main_window.get_active_editor()
		if(aed == None): return

		self.app.readjust()
		
		try:
			y, x = get_center_coords(self.app, 16, 30)
		except:
			self.app.warn_insufficient_screen_space()
			return

		self.app.dlgPreferences = ModalDialog(self.app.main_window, y, x, 16, 30, "PREFERENCES", self.preferences_key_handler)
		current_tab_size = str(aed.tab_size)
		txtTabSize = TextField(self.app.dlgPreferences, 3, 2, 26, current_tab_size, True)
		lstEncodings = ListBox(self.app.dlgPreferences, 5, 2, 26, 6)
		chkShowLineNumbers = CheckBox(self.app.dlgPreferences, 12, 2, "Show line numbers")
		chkWordWrap = CheckBox(self.app.dlgPreferences, 13, 2, "Word Wrap")
		chkHardWrap = CheckBox(self.app.dlgPreferences, 14, 2, "Hard Wrap")
		
		for enc in SUPPORTED_ENCODINGS:
			lstEncodings.add_item(("  " if aed.buffer.encoding != enc else TICK_MARK + " ") +  enc)
		
		chkShowLineNumbers.set_value(aed.show_line_numbers)
		chkWordWrap.set_value(aed.word_wrap)
		chkHardWrap.set_value(aed.hard_wrap)
		lstEncodings.sel_index = SUPPORTED_ENCODINGS.index(aed.buffer.encoding)
		
		self.app.dlgPreferences.add_widget("txtTabSize", txtTabSize)
		self.app.dlgPreferences.add_widget("lstEncodings", lstEncodings)
		self.app.dlgPreferences.add_widget("chkShowLineNumbers", chkShowLineNumbers)
		self.app.dlgPreferences.add_widget("chkWordWrap", chkWordWrap)
		self.app.dlgPreferences.add_widget("chkHardWrap", chkHardWrap)
		
		self.app.dlgPreferences.show()

	def preferences_key_handler(self, ch):
		aed = self.app.main_window.get_active_editor()

		if(is_ctrl(ch, "Q")): 
			self.app.dlgPreferences.hide()
		elif(is_newline(ch) or is_ctrl(ch, "W")):
			try:
				tab_size = int(str(self.app.dlgPreferences.get_widget("txtTabSize")))
			except:
				self.app.show_error("TAB SIZE", "Incorrect tab size: should be in [1,9]")
				return -1

			encoding_index = self.app.dlgPreferences.get_widget("lstEncodings").sel_index
			show_line_numbers = self.app.dlgPreferences.get_widget("chkShowLineNumbers").isChecked()
			word_wrap = self.app.dlgPreferences.get_widget("chkWordWrap").isChecked()
			hard_wrap = self.app.dlgPreferences.get_widget("chkHardWrap").isChecked()

			self.app.dlgPreferences.hide()

			if(tab_size < 1 or tab_size > 9):
				self.app.show_error("TAB SIZE", "Incorrect tab size: should be in [1,9]")
				return -1

			aed.tab_size = tab_size
			aed.buffer.set_encoding(SUPPORTED_ENCODINGS[encoding_index])
			aed.toggle_line_numbers(show_line_numbers)
			aed.set_wrap(word_wrap, hard_wrap)

			self.app.main_window.repaint()
			aed.repaint()
			return -1
		
		return ch

	# <----------------------------------- File New --------------------------------->

	def invoke_file_new(self):
		mw = self.app.main_window
		
		# create blank buffer
		new_bid, new_buffer = self.app.buffers.create_new_buffer()
		mw.invoke_activate_editor(new_bid, new_buffer)

	# <------------------------------------ Help --------------------------------------------->

	def invoke_help_key_bindings(self):
		self.app.readjust()

		try:
			y, x = get_center_coords(self.app, 20, 80)
		except:
			self.app.warn_insufficient_screen_space()
			return

		self.app.dlgHelpKeyBindings = ModalDialog(self.app.main_window, y, x, 20, 80, "HELP: KEY BINDINGS", self.help_key_bindings_key_handler)
		lstKeys = ListBox(self.app.dlgHelpKeyBindings, 3, 2, 76, 16)

		kbs = get_ash_key_bindings()
		for kb in kbs:
			key = kb[0].ljust(16)
			desc = kb[1]
			lstKeys.add_item(key + desc)

		self.app.dlgHelpKeyBindings.add_widget("lstKeys", lstKeys)
		self.app.dlgHelpKeyBindings.show()

	def help_key_bindings_key_handler(self, ch):
		if(is_ctrl(ch, "Q")):
			self.app.dlgHelpKeyBindings.hide()
			self.app.main_window.repaint()
			return -1
		return ch

	# <------------------------ File Open / Project Explorer --------------------------------->

	def invoke_project_explorer(self):
		self.app.readjust()
		try:
			y, x = get_center_coords(self.app, 20, 80)
		except:
			self.app.warn_insufficient_screen_space()
			return
		self.app.dlgProjectExplorer = ModalDialog(self.app.main_window, y, x, 20, 80, "PROJECT EXPLORER", self.project_explorer_key_handler)
		lstFiles = TreeView(self.app.dlgProjectExplorer, 3, 2, 76, 16, self.app.buffers, self.app.project_dir)
		self.app.dlgProjectExplorer.add_widget("lstFiles", lstFiles)
		self.app.dlgProjectExplorer.show()

	def project_explorer_key_handler(self, ch):
		lstFiles = self.app.dlgProjectExplorer.get_widget("lstFiles")
		
		mw = self.app.main_window
				
		if(is_ctrl(ch, "Q")):
			self.app.dlgProjectExplorer.hide()
			mw.repaint()
			return -1
		elif(is_newline(ch)):
			tag = lstFiles.get_sel_tag()		# format: {d/f}:path
			if(tag == None): return -1
			file_type = tag[0].lower()
			filename = tag[2:]
			if(file_type == "d"): return -1
						
			if(BufferManager.is_binary(filename)):
				self.app.show_error("Cannot open binary file!")
				mw.repaint()
				self.app.dlgProjectExplorer.repaint()
				return -1

			sel_buffer = self.app.buffers.get_buffer_by_filename(filename)
			if(sel_buffer == None):
				sel_bid, sel_buffer = self.app.buffers.create_new_buffer(filename=filename, has_backup=BufferManager.backup_exists(filename))
			
			self.app.dlgProjectExplorer.hide()
			mw.invoke_activate_editor(sel_buffer.id, sel_buffer)
			return -1
		
		return ch

	def invoke_file_open(self, target_ed_index = -1):
		self.app.readjust()

		try:
			y, x = get_center_coords(self.app, 14, 60)
		except:
			self.app.warn_insufficient_screen_space()
			return

		self.app.dlgFileOpen = ModalDialog(self.app.main_window, y, x, 14, 60, "OPEN FILE", self.file_open_key_handler)
		txtFileName = TextField(self.app.dlgFileOpen, 3, 2, 56, str(os.getcwd()) + "/")
		lstActiveFiles = ListBox(self.app.dlgFileOpen, 5, 2, 56, 6, "(No active files)")
		lstEncodings = ListBox(self.app.dlgFileOpen, 12, 2, 56, 1)

		# add the list of active files
		blist = self.app.buffers.get_list()
		for (bid, save_status, bname) in blist:
			lstActiveFiles.add_item((" " if save_status else UNSAVED_BULLET) + " " + get_file_title(bname), tag=bid)
			
		# add the encodings
		for enc in SUPPORTED_ENCODINGS:
			lstEncodings.add_item(enc)
		
		# set default encoding to UTF-8
		lstEncodings.sel_index = SUPPORTED_ENCODINGS.index("utf-8")

		self.app.dlgFileOpen.add_widget("txtFileName", txtFileName)
		self.app.dlgFileOpen.add_widget("lstActiveFiles", lstActiveFiles)
		self.app.dlgFileOpen.add_widget("lstEncodings", lstEncodings)
		
		self.app.target_open_ed_index = target_ed_index
		self.app.dlgFileOpen.show()

	def file_open_key_handler(self, ch):
		txtFileName = self.app.dlgFileOpen.get_widget("txtFileName")
		lstActiveFiles = self.app.dlgFileOpen.get_widget("lstActiveFiles")
		lstEncodings = self.app.dlgFileOpen.get_widget("lstEncodings")

		sel_bid = lstActiveFiles.get_sel_tag()
		sel_index = lstActiveFiles.get_sel_index()
		mw = self.app.main_window

		if(is_ctrl(ch, "Q")):
			self.app.dlgFileOpen.hide()
			mw.repaint()
			return -1
		elif(is_newline(ch)):
			is_buffer = False
			sel_buffer = None

			if(lstActiveFiles.is_in_focus and sel_index > -1):
				sel_buffer = self.app.buffers.get_buffer_by_id(sel_bid)
				is_buffer = True
				filename = sel_buffer.filename
			else:							
				filename = str(txtFileName)

			if(filename != None):
				if(os.path.isdir(filename)):
					self.app.show_error("Cannot open directory, relaunch with the directory-name as\nthe first argument to ash.")
					mw.repaint()
					self.app.dlgFileOpen.repaint()
					return -1

				if(BufferManager.is_binary(filename)):
					self.app.show_error("Cannot open binary file!")
					mw.repaint()
					self.app.dlgFileOpen.repaint()
					return -1
			
			sel_encoding = str(lstEncodings)
			self.app.dlgFileOpen.hide()
			
			if(not is_buffer):
				# it is a file
				if(not os.path.isfile(filename)):
					# file does not exist on disk
					response = self.app.ask_question("CREATE FILE", "The selected file does not exist, create?")
					if(not response): return -1

				sel_buffer = self.app.buffers.get_buffer_by_filename(filename)
				if(sel_buffer == None):
					# create buffer from file
					backup_status = BufferManager.backup_exists(filename)
					sel_bid, sel_buffer = self.app.buffers.create_new_buffer(filename=filename, encoding=sel_encoding, has_backup=backup_status)
				
			# at this point, buffer exists in sel_buffer
			mw.invoke_activate_editor(sel_buffer.id, sel_buffer)
			return -1
		
		return ch

	# <----------------------------------------------------------------------------------->

	# <----------------------------------- Show Active Tabs --------------------------------->

	def invoke_show_active_tabs(self):
		self.app.readjust()
		try:
			y, x = get_center_coords(self.app, 9, 40)
		except:
			self.app.warn_insufficient_screen_space()
			return
	
		self.app.dlgActiveTabs = ModalDialog(self.app.main_window, y, x, 9, 40, "ACTIVE TABS", self.show_active_tabs_key_handler)
		lstActiveTabs = ListBox(self.app.dlgActiveTabs, 3, 2, 36, 5, callback = self.active_tab_selection_changed)
		
		tabs_info = self.app.main_window.get_tabs_info()
		active_tab_index = self.app.main_window.get_active_tab_index()

		for i in range(len(tabs_info)):
			tab_name, ed_count = tabs_info[i]
			disp = tab_name + " (" + str(ed_count) + " editors)"
			if(i == active_tab_index):
				lstActiveTabs.add_item(TICK_MARK + " " + disp)
				lstActiveTabs.sel_index = i
			else:
				lstActiveTabs.add_item("  " + disp)
	
		self.app.old_active_tab_index = active_tab_index
		self.app.dlgActiveTabs.add_widget("lstActiveTabs", lstActiveTabs)
		self.app.dlgActiveTabs.show()

	def show_active_tabs_key_handler(self, ch):
		if(is_ctrl(ch, "Q")):
			self.app.dlgActiveTabs.hide()
			self.app.main_window.switch_to_tab(self.app.old_active_tab_index)
			self.app.main_window.repaint()
			return -1
		elif(is_newline(ch) or is_ctrl(ch, "W")):
			new_tab_index = self.app.dlgActiveTabs.get_widget("lstActiveTabs").get_sel_index()
			self.app.dlgActiveTabs.hide()
			self.app.main_window.switch_to_tab(new_tab_index)
			self.app.main_window.repaint()			
			return -1
			
		return ch

	def active_tab_selection_changed(self, new_tab_index):
		self.app.main_window.switch_to_tab(new_tab_index)
		self.app.main_window.repaint()

	# -------------------------------------------------------------------------------------


	# <----------------------------------- File Save As ---------------------------------->

	def invoke_file_save_as(self, buffer):
		self.app.readjust()

		try:
			y, x = get_center_coords(self.app, 5, 60)
		except:
			self.app.warn_insufficient_screen_space()
			return
			
		self.app.dlgSaveAs = ModalDialog(self.app.main_window, y, x, 5, 60, "SAVE AS", self.file_save_as_key_handler)
		if(buffer.filename == None): 
			filename = str( self.app.project_dir if self.app.app_mode == APP_MODE_PROJECT else os.getcwd() ) + "/" + buffer.get_name()
		else:
			filename = get_copy_filename(buffer.filename)
		txtFileName = TextField(self.app.dlgSaveAs, 3, 2, 56, filename)
		self.app.dlgSaveAs_Buffer = buffer
		self.app.dlgSaveAs.add_widget("txtFileName", txtFileName)
		self.app.dlgSaveAs.show()

	def file_save_as_key_handler(self, ch):
		if(is_ctrl(ch, "Q")): 
			self.app.dlgSaveAs.hide()
			return -1
		elif(is_newline(ch)):
			buffer = self.app.dlgSaveAs_Buffer
			self.app.dlgSaveAs.hide()
			txtFileName = self.app.dlgSaveAs.get_widget("txtFileName")
			filename = str(txtFileName)

			if(not os.path.isfile(filename)):
				buffer.write_to_disk(filename)
			else:
				if(self.app.ask_question("REPLACE FILE", "File already exists, replace?")):
					buffer.write_to_disk(filename)
			return -1
					
		return ch