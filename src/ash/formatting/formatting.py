# ---------------------------------------------------------------------------------------------
#  Copyright (c) Akash Nag. All rights reserved.
#  Licensed under the MIT License. See LICENSE.md in the project root for license information.
# ---------------------------------------------------------------------------------------------

# This module handles all text formatting for the application

from ash.formatting import *

# chop off a string if it exceeds maxlen and end it with "..."
def pad_str_max(data, maxlen):
	n = len(data)
	if(n <= maxlen):
		return data
	else:
		return data[0:maxlen-3] + "..."

def is_all_hex(s):
	s = s.lower()
	n = len(s)
	for i in range(n):
		x = ord(s[i])
		if((x >= 48 and x<=57) or (x >= 97 and x <= 102)): continue
		return False
	return True

def get_unicode_encoded_line(line):
	n = len(line)
	i = 0
	
	while(i < n-5):
		if(line[i:i+2] == "\\u" and is_all_hex(line[i+2:i+6])):
			part = line[i:i+6]
			enc_part = bytes(part, "utf-8").decode("unicode_escape")
			line = line[0:i] + enc_part + line[i+6:]
			n = len(line)
		i += 1

	return line

def unicode_escape(s):
	return bytes(s, "utf-8").decode("unicode_escape")

def get_circled_letter(letter):
	u = ord(letter)
	if(u >= 65 and u <= 90):
		base = 0x24b6 + (u - 65)
	elif(u >= 97 and u <= 122):
		base = 0x24d0 + (u - 97)
	else:
		return None	
	return unicode_escape("\\u" + hex(base)[2:])