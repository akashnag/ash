# SPDX-License-Identifier: GPL-2.0-only
#
# /src/ash/utils/__init__.py
#
# Copyright (C) 2022-2022  Akash Nag

import sys
import curses
import subprocess
import os
import copy
import codecs
import chardet
import mimetypes

from datetime import datetime

from ash import *
from ash.core.logger import *