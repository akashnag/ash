from ash import *

APP_MODE_BLANK		= 1
APP_MODE_FILE		= 2
APP_MODE_PROJECT	= 3

class AshEditorApp:
	def __init__(self, args):
		self.args = args
		
	def run(self):
		# check arguments and set flags
		pass

		# show GUI
		curses.wrapper(self.app_main)

	def app_main(self, stdscr):
		init_colors()
		curses.raw()
		
		self.main_window = TopLevelWindow(stdscr, "Ash v1.0", gc(COLOR_WHITE_ON_BLUE), self.key_handler)
		self.main_window.add_status_bar(StatusBar(self.main_window, [ 1.0 ]))		
		
		#self.main_window.add_widget("lblName", Label(self.main_window, 3, 2, "Name: ", gc()))
		#self.main_window.add_widget("txtName", TextArea(self.main_window, 3, 10, 10, 30, gc(COLOR_YELLOW_ON_BLACK), gc(COLOR_BLACK_ON_YELLOW)))
		
		txtEditor = Editor(self.main_window, 1, 0, self.main_window.get_height()-2, self.main_window.get_width())
		txtEditor.set_general_theme(gc(), gc(COLOR_BLACK_ON_YELLOW), gc(COLOR_GRAY_ON_BLACK), gc(COLOR_YELLOW_ON_BLACK))

		self.main_window.add_widget("txtEditor", txtEditor)

		self.main_window.show()
		
	def key_handler(self, ch):
		if(is_ctrl(ch, "Q")):
			self.main_window.hide()
		else:
			#x = str(self.main_window.get_widget("txtName"))
			#self.main_window.get_status_bar().set(0, str(curses.keyname(ch)))
			txtEditor = self.main_window.get_widget("txtEditor")
			nlen = len(txtEditor.lines[txtEditor.curpos.y])
			self.main_window.get_status_bar().set(0, str(txtEditor.selection_mode) + " -> " + str(txtEditor.sel_start) + " : " + str(txtEditor.sel_end))
			#self.main_window.win.addstr(1,1, str(self.main_window.get_widget("txtName")), gc())
		return ch
