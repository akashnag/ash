# ---------------------------------------------------------------------------------------------
#  Copyright (c) Akash Nag. All rights reserved.
#  Licensed under the MIT License. See LICENSE.md in the project root for license information.
# ---------------------------------------------------------------------------------------------

# This is a helper module to assist with various dialogs

from ash import *

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
		# 		(a) No other editors exist: quit application
		# 		(b) Other editors exist: inform user that other editors exist

		if(aed == None):
			# case 3
			n = len(mw.editors)
			other_editors_exist = False
			for i in range(n):
				if(mw.editors[i] != None):
					other_editors_exist = True
					break
			
			if(other_editors_exist):
				# case 3(b)
				self.app.show_error("Close all windows to quit application or use Ctrl+@ to force-quit")
			else:
				# case 3(a)
				mw.hide()
		else:
			if(aed.save_status):
				# case 1
				filename = aed.filename
				buffer_index = get_file_buffer_index(self.app.files, filename)
				filedata = aed.get_data()
				self.app.files[buffer_index] = filedata
				mw.close_active_editor()
			else:
				if(not aed.has_been_allotted_file):
					# case 2(a)
					if(self.app.ask_question("DISCARD CHANGES", "Do you want to save this file (Yes) or discard changes (No)?")):
						self.invoke_file_save_as()
						if(aed.save_status): 
							# no need to add this filedata to list of active files as
							# invoke_file_save_as() already does it
							mw.close_active_editor()
					else:
						mw.close_active_editor()
				else:
					# case 2(b) [same as case 1]
					filename = aed.filename
					buffer_index = get_file_buffer_index(self.app.files, filename)
					filedata = aed.get_data()
					self.app.files[buffer_index] = filedata
					mw.close_active_editor()

	# <----------------------------------- File Open --------------------------------->

	def invoke_project_file_open(self):
		pass

	def invoke_file_open(self):
		self.app.readjust()
		y, x = get_center_coords(self.app, 11, 40)
		self.app.dlgFileOpen = ModalDialog(self.app.stdscr, y, x, 11, 40, "OPEN FILE", self.file_open_key_handler)
		txtFileName = TextField(self.app.dlgFileOpen, 2, 2, 36, str(os.getcwd()) + "/")
		lstActiveFiles = ListBox(self.app.dlgFileOpen, 4, 2, 36, 6)
		for f in self.app.files:
			lstActiveFiles.add_item(get_file_title(f.filename))
		self.app.dlgFileOpen.add_widget("txtFileName", txtFileName)
		self.app.dlgFileOpen.add_widget("lstActiveFiles", lstActiveFiles)
		self.app.dlgFileOpen.show()		

	def file_open_key_handler(self, ch):
		if(is_ctrl(ch, "Q")):
			self.app.dlgFileOpen.hide()
			return -1
		elif(is_newline(ch)):
			self.app.dlgFileOpen.hide()
			return -1
		else:
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
			else:
				lstLayouts.add_item(layouts[i])

		self.app.dlgSwitchLayout.add_widget("lstLayouts", lstLayouts)
		self.app.dlgSwitchLayout.show()

	def switch_layout_key_handler(self, ch):
		if(is_ctrl(ch, "Q")):
			self.app.dlgSwitchLayout.hide()
		elif(is_newline(ch)):
			new_layout = self.app.dlgSwitchLayout.get_widget("lstLayouts").get_sel_index()
			self.app.dlgSwitchLayout.hide()

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
		y, x = get_center_coords(self.app, 4, 40)
		self.app.dlgSaveAs = ModalDialog(self.app.stdscr, y, x, 4, 40, "SAVE AS", self.file_save_as_key_handler)
		if(filename == None): filename = str(os.getcwd()) + "/untitled.txt"
		txtFileName = TextField(self.app.dlgSaveAs, 2, 2, 36, filename)
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