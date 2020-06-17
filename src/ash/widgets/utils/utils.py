from ash.widgets.utils import *

def is_ctrl(ch, key):
	key = str(key).upper()
	sch = str(curses.keyname(ch))
	return(True if sch == "b'^" + key + "'" else False)

def is_ctrl_or_func(ch):
	sch = str(curses.keyname(ch))
	return(True if sch.startswith("b'KEY_F(") or sch.startswith("b'^") or (sch.startswith("b'k") and sch.endswith("5'")) else False)
	
def is_newline(ch):
	return (ch == curses.KEY_ENTER or is_ctrl(ch, "J"))

def is_tab(ch):
	return (ch == curses.KEY_STAB or is_ctrl(ch, "I"))

def is_ctrl_arrow(ch, arrow = None):
	sch = str(curses.keyname(ch))
	if(arrow == None):
		return (True if (sch == "b'kUP5'" or sch == "b'kDN5'" or sch == "b'kLFT5'" or sch == "b'kRIT5'") else False)
	else:
		sarrow = str(arrow).upper()
		
		if(sch == "b'kUP5'" and sarrow == "UP"):
			return True
		elif(sch == "b'kDN5'" and sarrow == "DOWN"):
			return True
		elif(sch == "b'kLFT5'" and sarrow == "LEFT"):
			return True
		elif(sch == "b'kRIT5'" and sarrow == "RIGHT"):
			return True
		else:
			return False

def is_start_before_end(start, end):
	if(start.y == end.y and start.x < end.x): return True
	if(start.y < end.y): return True
	return False