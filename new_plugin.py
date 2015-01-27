from __future__ import print_function
import sublime, sublime_plugin
import os, sys, imp
import subprocess


#PACKAGE_PARENT = ""
SCRIPT_DIR = os.path.dirname(os.path.realpath(os.path.join(os.getcwd(), os.path.expanduser(__file__))))
#sys.path.append(os.path.normpath(os.path.join(SCRIPT_DIR, PACKAGE_PARENT)))
#sys.path.append(os.path.join(os.path.dirname(__file__),"MAGSBS"))

import MAGSBS as magsbs

#import MAGSBS.matuc as matuc
#from MAGSBS.pandoc import *
#from MAGSBS.quality_assurance import *
# from MAGSBS.filesystem import *
# from MAGSBS.master import *
# from MAGSBS.mparser import *
# from MAGSBS.config import *
# from MAGSBS.errors import *
# from MAGSBS.datastructures import *
# from MAGSBS.contentfilter import *


# from MAGSBS/__init__.py
#__all__ = ["pandoc", "quality_assurance", "filesystem", "mparser",
#       "errors", "datastructures", "contentfilter", "config"]

class AgsbsCommand(sublime_plugin.TextCommand):
	def run(self, edit):
		#print(os.path.join(os.path.dirname(__file__),"MAGSBS"))
		#print(dir(magsbs.master))
		m = magsbs.master.Master(SCRIPT_DIR)
		#matuc.
		#self.subProc()

	def subProc(self):
		print(subprocess.call("dir",shell = True))
		








