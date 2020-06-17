from ash.widgets.utils import *
from datetime import datetime

COLOR_WHITE_ON_BLACK 	= 1
COLOR_WHITE_ON_RED 		= 2
COLOR_WHITE_ON_GREEN 	= 3
COLOR_RED_ON_BLACK 		= 4
COLOR_GREEN_ON_BLACK 	= 5
COLOR_YELLOW_ON_BLACK 	= 6
COLOR_BLACK_ON_YELLOW 	= 7
COLOR_BLACK_ON_WHITE	= 8
COLOR_WHITE_ON_BLUE		= 9
COLOR_BLUE_ON_BLACK		= 10
COLOR_GRAY_ON_BLACK		= 11
COLOR_DIMWHITE_ON_BLACK	= 12

def init_colors():
	curses.init_color(0, 0, 0, 0)

	curses.init_color(curses.COLOR_BLACK, 0, 0, 0)
	curses.init_color(curses.COLOR_WHITE, 999, 999, 999)
	curses.init_color(curses.COLOR_RED, 999, 0, 0)
	curses.init_color(curses.COLOR_GREEN, 0, 999, 0)
	curses.init_color(curses.COLOR_BLUE, 0, 478, 796)
	curses.init_color(curses.COLOR_YELLOW, 999, 999, 0)
	
	# different color mapping
	curses.init_color(curses.COLOR_MAGENTA, 426, 426, 426)		# light gray
	curses.init_color(curses.COLOR_CYAN, 856, 856, 856)		# dim white
	curses.init_pair(COLOR_GRAY_ON_BLACK, curses.COLOR_MAGENTA, curses.COLOR_BLACK)
	curses.init_pair(COLOR_DIMWHITE_ON_BLACK, curses.COLOR_CYAN, curses.COLOR_BLACK)
	# -------------------------

	curses.init_pair(COLOR_WHITE_ON_BLACK, curses.COLOR_WHITE, curses.COLOR_BLACK)
	curses.init_pair(COLOR_WHITE_ON_RED, curses.COLOR_WHITE, curses.COLOR_RED)
	curses.init_pair(COLOR_WHITE_ON_GREEN, curses.COLOR_WHITE, curses.COLOR_GREEN)
	curses.init_pair(COLOR_RED_ON_BLACK, curses.COLOR_RED, curses.COLOR_BLACK)
	curses.init_pair(COLOR_GREEN_ON_BLACK, curses.COLOR_GREEN, curses.COLOR_BLACK)
	curses.init_pair(COLOR_YELLOW_ON_BLACK, curses.COLOR_YELLOW, curses.COLOR_BLACK)
	curses.init_pair(COLOR_BLACK_ON_YELLOW, curses.COLOR_BLACK, curses.COLOR_YELLOW)
	curses.init_pair(COLOR_BLACK_ON_WHITE, curses.COLOR_BLACK, curses.COLOR_WHITE)
	curses.init_pair(COLOR_WHITE_ON_BLUE, curses.COLOR_WHITE, curses.COLOR_BLUE)
	curses.init_pair(COLOR_BLUE_ON_BLACK, curses.COLOR_BLUE, curses.COLOR_BLACK)

def pad_amount_signed(data, maxlen=8):
	if(data == None):
		sdata = "-"
	else:
		sdata = str(data)
	if(data != 0 and (not sdata.startswith("-"))): sdata = "+" + sdata
	pos = sdata.find(".")
	if(pos > -1):
		frac = sdata[pos+1:]
		if(len(frac)<2):
			sdata += "0"
		elif(len(frac)>2):
			sdata = sdata[0:pos+3]
	
	delta = maxlen - len(sdata)
	if(delta < 0):
		return sdata + " "
	else:
		return (" " * (delta+1)) + sdata + " "

def pad_amount(data, maxlen=8):
	if(data == None):
		sdata = "-"
	else:
		sdata = str(data)
	pos = sdata.find(".")
	if(pos > -1):
		frac = sdata[pos+1:]
		if(len(frac)<2):
			sdata += "0"
		elif(len(frac)>2):
			sdata = sdata[0:pos+3]
	
	delta = maxlen - len(sdata)
	if(delta < 0):
		return sdata + " "
	else:
		return (" " * (delta+1)) + sdata + " "

def get_color_bg(old_data, new_data):
	if(old_data == None or new_data == None or old_data == new_data):
		return curses.color_pair(COLOR_BLACK_ON_WHITE)
	elif(new_data > old_data):
		return curses.color_pair(COLOR_WHITE_ON_GREEN)
	else:
		return curses.color_pair(COLOR_WHITE_ON_RED)

def get_color_fg(data):
	if(data == None or data == 0):
		return curses.color_pair(COLOR_WHITE_ON_BLACK)
	elif(data > 0):
		return curses.color_pair(COLOR_GREEN_ON_BLACK)
	else:
		return curses.color_pair(COLOR_RED_ON_BLACK)

def get_current_time():
	fmt = "%H:%M:%S"
	now = datetime.now()
	return now.strftime(fmt)

def is_market_closed():
	fmt = "%H:%M"
	now = datetime.now()
	ctime = now.strftime(fmt)
	w = int(now.strftime("%w"))
	if(w == 0 or w == 6): return True

	marker1 = "15:30"
	marker2 = "09:15"
	
	delta1 = datetime.strptime(marker1,fmt) - datetime.strptime(ctime,fmt)
	delta2 = datetime.strptime(ctime,fmt) - datetime.strptime(marker2,fmt)
	delta3 = datetime.strptime(marker2,fmt) - datetime.strptime(ctime,fmt)

	# 8am = delta1 +ve, delta2 -ve, delta3 +ve
	# 10am = delta1 +ve, delta2 +ve, delta3 -ve 
	# 5pm = delta1 -ve, delta2 +ve, delta3 -ve

	if(delta1.total_seconds() >= 0 and delta2.total_seconds() < 0):
		# before 9:15am
		x = str(delta3)
		y = datetime.strptime(x, "%H:%M:%S")
		#return y.strftime(fmt) + " to open"
		return True
	elif(delta1.total_seconds() >= 0 and delta2.total_seconds() >= 0):
		# between 9:15am and 3:15pm
		x = str(delta1)
		y = datetime.strptime(x, "%H:%M:%S")
		#return y.strftime(fmt) + " to close"
		return False
	elif(delta1.total_seconds() < 0 and delta2.total_seconds() >= 0):
		# between 3:15pm and 12am
		#return "market closed"
		return True

def pretty(amt, dec=True):
	# convert 1171554.76 to 11,71,554.76
	if(amt == None): return "-"

	samt = str(amt)
	decpos = samt.find(".")
	if(decpos == -1 and dec==True):
		frac = ".00"
	elif(decpos == -1 and dec==False):
		frac = ""
	elif(decpos > -1):
		frac = samt[decpos:]
		if(len(frac) == 2): frac = frac + "0"
	
	if(decpos == -1):
		whole = samt
	else:
		whole = samt[0:decpos]
	
	#  1715542814
	#  9876543210
	if(len(whole) < 4 or (whole.startswith("-") and len(whole)==4)):
		return whole + frac
	elif(len(whole) < 6 or (whole.startswith("-") and len(whole)==6)):
		# 1546		12574	-12345
		# 0123		01234
		if(len(whole)==4):
			return whole[0] + "," + whole[1:] + frac
		elif(len(whole)==5):
			return whole[0:2] + "," + whole[2:] + frac
		else:
			return whole[0:3] + "," + whole[3:] + frac
	else:
		# 1.14.47.55|899		len=10
		# 0.12.34.56|789		i= 6 5 4 3 2 1 0
		# 9.87.65.43|210		j= 0 1 2 3 4 5 6
		s = whole[len(whole)-3:]
		for i in range(len(whole)-4, -1, -1):
			j = len(whole) - i - 4
			if(j % 2 == 0 and whole[i] != "-" and whole[i] != "+"):
				s = whole[i] + "," + s
			else:
				s = whole[i] + s
		
		if(s.startswith(",")): s = s[1:]
		return s+frac

def gc(cp = COLOR_WHITE_ON_BLACK):
	return curses.color_pair(cp)

# <----------------------- string padding functions ----------------->
def pad_left_str(data, width):
	sdata = str(data)
	n = len(sdata)
	if(n < width):
		return (" " * (width-n)) + sdata
	else:
		return sdata

def pad_right_str(data, width):
	sdata = str(data)
	n = len(sdata)
	if(n < width):
		return sdata + (" " * (width-n))
	else:
		return sdata

def pad_str_max(data, maxlen):
	n = len(data)
	if(n <= maxlen):
		return data
	else:
		return data[0:maxlen-3] + "..."

def pad_center_str(str, maxlen):
	if(len(str) >= maxlen):
		return str
	else:
		pad = (maxlen - len(str)) // 2
		return (" " * pad) + str + (" " * pad)