# ---------------------------------------------------------------------------------------------
#  Copyright (c) Akash Nag. All rights reserved.
#  Licensed under the MIT License. See LICENSE.md in the project root for license information.
# ---------------------------------------------------------------------------------------------

# This is a helper module to assist with various dialogs

from ash import *

UNSAVED_BULLET		= "\u2022 "

class DialogHandler:
	def __init__(self, app):
		self.app = app

	# <----------------------------------- Go to Line --------------------------------->

	def invoke_go_to_line(self):
		self.app.readjust()
		y, x = get_center_coords(self.app, 4, 14)
		self.app.dlgGoTo = ModalDialog(self.app.stdscr, y, x, 4, 14, "GO TO LINE", self.go_to_key_handler)
		currentLine = str(self.app.main_window.get_active_editor().curpos.y + 1)
		txtLineNumber = TextField(self.app.dlgGoTo, 2, 2, 10, currentLine, True)
		self.app.dlgGoTo.add_widget("txtLineNumber", txtLineNumber)
		self.app.dlgGoTo.show()

	def go_to_key_handler(self, ch):
		if(is_ctrl(ch, "Q")): 
			self.app.dlgGoTo.hide()
		elif(is_newline(ch)):
			line = str(self.app.dlgGoTo.get_widget("txtLineNumber"))
			if(len(line) == 0):
				beep()
				return ch

			pos = line.find(".")
			if(pos > -1):
				row = int(line[0:pos]) - 1
				col = int(line[pos+1:]) - 1
			else:
				row = int(line) - 1
				col = 0
			
			aed = self.app.main_window.get_active_editor()
			if(row < 0 or row >= len(aed.lines)):
				beep()
			elif(col < 0 or col > len(aed.lines[row])):
				beep()
			else:
				self.app.dlgGoTo.hide()
				aed.curpos.y = row
				aed.curpos.x = col
				aed.repaint()
		
		return ch

	# <----------------------------------- Close Editor/App --------------------------------->

	def invoke_forced_quit(self):
		self.app.main_window.hide()

	def invoke_quit(self):
		mw = self.app.main_window
		aed = mw.get_active_editor()

		# Scenarios:
		# 1. Active editor is saved: close editor (maintain buffer)
		# 2. Active editor is unsaved: check if file-allotted or not
		#		(a) if no file allotted: ask to be saved first, before closing
		#		(b)	if file allotted: close editor (maintain buffer)
		# 3. No active editor: check if other editors exist:
		# 		(a) No other editors exist: check if unsaved files exist
		# 			(i) no unsaved files exist: quit application
		#			(ii) unsaved files exist: ask user (Yes: save-all, No: discard-all, Cancel: dont-quit)
		# 		(b) Other editors exist: inform user that other editors exist

		if(aed == None):
			# case 3: no active editor exists
			n = len(mw.editors)
			other_editors_exist = False
			for i in range(n):
				if(mw.editors[i] != None):
					other_editors_exist = True
					break
			
			if(other_editors_exist):
				# case 3(b): other editors exist
				self.app.show_error("Close all windows to quit application or use Ctrl+@ to force-quit")
			else:
				# case 3(a): no other editors exist
				all_saved = True
				for f in self.app.files:
					if(not f.save_status):
						all_saved = False
						break

				if(all_saved):
					# case 3(a)[i]: all buffers saved: quit app
					mw.hide()
				else:
					# case 3(a)[ii]: some buffers are unsaved: confirm with user
					response = self.app.ask_question("SAVE/DISCARD ALL", "One or more unsaved files exist, choose yes(save-all) / no(discard-all) / cancel(dont-quit)", True)
					if(response == None):
						return
					elif(response):
						write_all_buffers_to_disk(self.app.files)
						mw.hide()
						return
					elif(not response):
						mw.hide()
						return
		else:
			if(aed.save_status):
				# case 1: active editor is saved
				save_to_buffer(self.app.files, aed)
				mw.close_active_editor()
			else:
				# case 2: active editor has unsaved changes
				if(not aed.has_been_allotted_file):
					# active editor does not have any allotted file
					if(aed.can_quit()):
						# still if can close (i.e. editor is blank: no data), then close editor
						mw.close_active_editor()
					else:
						# case 2(a): has unsaved changes: confirm with user
						response = self.app.ask_question("DISCARD CHANGES", "Do you want to save this file (Yes) or discard changes (No)?", True)
						if(response == None): return
						if(response):
							# user wants to save before closing: so show file-save-as dialogbox
							self.invoke_file_save_as()
							if(aed.save_status): 
								# no need to add this filedata to list of active files as
								# invoke_file_save_as() already does it
								mw.close_active_editor()
						else:
							# user wants to discard changes
							mw.close_active_editor()
				else:
					# case 2(b) [same as case 1]: active editor has been allotted file
					# so: save the contents into mapped buffer and close editor
					filename = aed.filename
					buffer_index = get_file_buffer_index(self.app.files, filename)
					filedata = aed.get_data()
					self.app.files[buffer_index] = filedata
					mw.close_active_editor()

	def invoke_file_new(self):
		mw = self.app.main_window
		aed = mw.get_active_editor()
		aedi = mw.active_editor_index

		if(aed == None or (not aed.can_quit() and not aed.has_been_allotted_file)):
			# no active-editor exists OR it is an unsaved buffer
			# so: look for a different editor to place the new file
			ffedi = get_first_free_editor_index(mw)
			if(ffedi == -1):
				# no other editor also exists
				self.app.show_error("No free editors available: switch layout or close an editor")
				return -1

			# different editor found, make it the active editor
			mw.layout_manager.invoke_activate_editor(ffedi)
			aed = mw.get_active_editor()
		else:
			# active editor has allotted-file and can be quit
			
			# so: save recent changes to buffer
			save_to_buffer(self.app.files, aed)

			# close and reopen
			mw.editors[aedi] = None
			mw.layout_manager.invoke_activate_editor(aedi)

		mw.repaint()
		
	# <----------------------------------- File Open --------------------------------->

	def invoke_project_file_open(self):
		pass

	def invoke_file_open(self):
		self.app.readjust()
		y, x = get_center_coords(self.app, 11, 60)
		self.app.dlgFileOpen = ModalDialog(self.app.stdscr, y, x, 11, 60, "OPEN FILE", self.file_open_key_handler)
		txtFileName = TextField(self.app.dlgFileOpen, 2, 2, 56, str(os.getcwd()) + "/")
		lstActiveFiles = ListBox(self.app.dlgFileOpen, 4, 2, 56, 6)
		for f in self.app.files:
			lstActiveFiles.add_item(("   " if f.save_status else UNSAVED_BULLET) +  get_file_title(f.filename))
		self.app.dlgFileOpen.add_widget("txtFileName", txtFileName)
		self.app.dlgFileOpen.add_widget("lstActiveFiles", lstActiveFiles)
		self.app.dlgFileOpen.show()		

	def file_open_key_handler(self, ch):
		txtFileName = self.app.dlgFileOpen.get_widget("txtFileName")
		lstActiveFiles = self.app.dlgFileOpen.get_widget("lstActiveFiles")
		sel_index = lstActiveFiles.get_sel_index()
		mw = self.app.main_window
		aed = mw.get_active_editor()

		if(is_ctrl(ch, "Q")):
			self.app.dlgFileOpen.hide()
			return -1
		elif(is_newline(ch)):
			if(lstActiveFiles.is_in_focus and sel_index > -1): txtFileName.set_text(self.app.files[sel_index].filename)
			filename = str(txtFileName)
			self.app.dlgFileOpen.hide()
			
			if(not file_exists_in_buffer(self.app.files, filename)):
				# new file is being opened
				if(os.path.isfile(filename)):
					# file exists on disk
					self.app.files.append(FileData(filename))
				else:
					# file does not exist
					self.app.show_error("The selected file does not exist")
					return -1

			if(aed == None or (not aed.can_quit() and not aed.has_been_allotted_file)):
				# no active-editor OR it is an unsaved-buffer
				# so: look for a different editor to place the new file
				ffedi = get_first_free_editor_index(mw)
				if(ffedi == -1):
					# no other editor also exists
					self.app.show_error("No free editors available: switch layout or close an editor")
					return -1

				# different editor found, make it the active editor
				mw.layout_manager.invoke_activate_editor(ffedi)
				aed = mw.get_active_editor()
			elif(not aed.can_quit() and aed.has_been_allotted_file):
				save_to_buffer(self.app.files, aed)
					
			bi = get_file_buffer_index(self.app.files, filename)
			aed.set_data(self.app.files[bi])
			aed.repaint()
			
			return -1
		elif(is_tab(ch) or ch == curses.KEY_BTAB):
			if(sel_index > -1): txtFileName.set_text(self.app.files[sel_index].filename)			
		
		return ch

	# <----------------------------------------------------------------------------------->

	# <----------------------------------- Switch Layout --------------------------------->

	def invoke_switch_layout(self):
		self.app.readjust()
		y, x = get_center_coords(self.app, 8, 40)
		self.app.dlgSwitchLayout = ModalDialog(self.app.stdscr, y, x, 8, 40, "SWITCH LAYOUT", self.switch_layout_key_handler)
		
		lstLayouts = ListBox(self.app.dlgSwitchLayout, 2, 2, 36, 5)
		layouts = 	[ 
					"Single", "Horizontal-2", "Horizontal-3", "Horizontal-4",
					"Vertical-2", "2x2", "2x3", "1-Left, 2-Right", "2-Left, 1-Right",
					"1-Top, 2-Bottom", "2-Top, 1-Bottom"
					]

		for i in range(len(layouts)):
			if(self.app.main_window.layout_type == i):
				lstLayouts.add_item("\u2713 " + layouts[i])
				lstLayouts.sel_index = i
			else:
				lstLayouts.add_item("  " + layouts[i])

		self.app.dlgSwitchLayout.add_widget("lstLayouts", lstLayouts)
		self.app.dlgSwitchLayout.show()

	def switch_layout_key_handler(self, ch):
		if(is_ctrl(ch, "Q")):
			self.app.dlgSwitchLayout.hide()
			self.app.main_window.repaint()
			return -1
		elif(is_newline(ch)):
			new_layout = self.app.dlgSwitchLayout.get_widget("lstLayouts").get_sel_index()
			self.app.dlgSwitchLayout.hide()
			self.app.main_window.repaint()

			if(new_layout == self.app.main_window.layout_type):				
				return -1
			elif(self.app.main_window.layout_manager.can_change_layout(new_layout)):
				self.app.main_window.layout_manager.set_layout(new_layout)
				return -1
			else:
				return self.app.show_error("One or more files need to be saved first")				
		return ch

	# -------------------------------------------------------------------------------------


	# <----------------------------------- File Save As ---------------------------------->

	def invoke_file_save_as(self, filename=None):
		self.app.readjust()
		y, x = get_center_coords(self.app, 4, 60)
		self.app.dlgSaveAs = ModalDialog(self.app.stdscr, y, x, 4, 60, "SAVE AS", self.file_save_as_key_handler)
		if(filename == None): filename = str(os.getcwd()) + "/untitled.txt"
		txtFileName = TextField(self.app.dlgSaveAs, 2, 2, 56, filename)
		self.app.dlgSaveAs.add_widget("txtFileName", txtFileName)
		self.app.dlgSaveAs.show()

	def file_save_as_key_handler(self, ch):
		if(is_ctrl(ch, "Q")): 
			self.app.dlgSaveAs.hide()
		elif(is_newline(ch)):
			self.app.dlgSaveAs.hide()
			txtFileName = self.app.dlgSaveAs.get_widget("txtFileName")
			if(not os.path.isfile(str(txtFileName))):
				self.save_or_overwrite(str(txtFileName))
			else:				
				if(self.app.ask_question("REPLACE FILE", "File already exists, replace?")):
					self.save_or_overwrite(str(txtFileName))
					
		return ch

	def save_or_overwrite(self, filename):
		self.app.dlgSaveAs.hide()
		try:
			self.app.main_window.do_save_as(filename)
		except Exception as e:
			self.app.show_error("An error occurred while saving file")			

	# --------------------------------------------------------------------------------------