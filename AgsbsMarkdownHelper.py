from __future__ import print_function
import sublime, sublime_plugin
import sys
import os
import re
import codecs, re, sys
import collections

VERSION = int(sublime.version())

reloader = "reloader"

if VERSION > 3000:
	print("sublime version is higher >= 3")
	#from .MAGSBS-infrastructure.MAGSBS import reloader	
	#from .MAGSBS.master import *
	from .agsbs_infrastructure.MAGSBS.master import *
	from .agsbs_infrastructure.MAGSBS.config import *
	from .agsbs_infrastructure.MAGSBS.errors import *
	from .agsbs_infrastructure.MAGSBS.filesystem import *
	from .agsbs_infrastructure.MAGSBS.mparser import *
	from .agsbs_infrastructure.MAGSBS.errors import *
	from .agsbs_infrastructure.MAGSBS.pandocfilters import *
	from .agsbs_infrastructure.MAGSBS.pandoc import *
	#from .MAGSBS.config import *
	#from  .MAGSBS.quality_assurance import *
	#from .MAGSBS.matuc import *
	#from .MAGSBS.lib.enum import *
	
else: 
	print("sublime version  < 3")
	from MAGSBS import reloader
	from MAGSBS.master import *

# Make sure all dependencies are reloaded on upgrade
if reloader in sys.modules:
    reload(sys.modules[reloader])



### Start plugin


settings = sublime.load_settings("Agsbshelper.sublime-settings")
global Debug
Debug = settings.get("debug")
global console

"""
{ "keys": ["F2"], "command": "create_structure", "args": {"tag": ""} }
"""
class CreateStructureCommand(sublime_plugin.TextCommand):
    def run(self,edit):
    	#raise NotImplementedError("CreateStructureCommand")
    	path = os.path.dirname(self.view.window().active_view().file_name())
    	if(Debug):
    		console = Console(self.view)
    		console.printMessage(self.view,path)    		
    		for key in sys.modules.keys():
    			if key.startswith("AgsbsMarkdownPlugin"):
    				print(key)
    		path = os.path.join(sublime.packages_path())
    		print(path)
    		m = Master(path)
    		#m.run()

"""
{ "keys": ["f3"], "command": "cmd" , "args": {"function": "checkMarkdown"} }
{ "keys": ["f5"], "command": "cmd", "args": {"function": "createHTML"} }
{ "keys": ["f6"], "command": "cmd", "args": {"function": "createAll"} } 
{ "keys": ["f7"], "command": "cmd", "args": {"function": "showHTML"} }
"""
class CmdCommand(sublime_plugin.TextCommand):
    def run(self, edit,function): 
    	view = self.view
    	debug_message = ""
    	if function == "checkMarkdown":
    		debug_message = "todo " + function
    	elif function == "createHTML":
    		#create html from open md.file
    		p = pandoc()
    		md_file = self.view.window().active_view().file_name()

    		debug_message = "md_file " +md_file 		
    		print()
    	elif function == "createAll":
    		debug_message = "todo " + function
    	elif function == "showHTML":
    		debug_message = "todo " + function
    	
    	if(Debug):
    		console = Console(self.view)
    		console.printMessage(self.view,debug_message)
"""
{ "keys": ["ctrl+alt+i"], "command": "insert_panel", "args": {"tag": "img"}},
"""
class InsertPanelCommand(sublime_plugin.TextCommand):   
	def run(self, edit, tag):		
		if tag == "img":
			# add content to dictionary
			self.image_url =""
			
			if(settings.get("hints")):
				sublime.message_dialog("Sie wollen ein Bild hinzufügen. Sie müssen 2 Eingaben tätigen: \n"
					"\t1. Speicherort des Bildes \n"
					"\t2. Alternativbeschreibung zum Bild \n")
			imageFormats = settings.get("image_formats")
			global imagefiles
			imagefiles = self.getFileName(imageFormats)
			self.show_prompt(imagefiles,tag)
	def show_prompt(self, listFile,tag):
		if tag == "img":
			self.view.window().show_quick_panel(listFile,self.on_done_filename,sublime.MONOSPACE_FONT)
		elif tag == "a":
			print("todo")


	def getFileName(self, imageFormats):
		listFiles = []
		filename = self.view.file_name()
		dir = os.path.dirname(filename)

		for root, dirs, files in os.walk(dir):
			for file in files:
				extension = os.path.splitext(file)[1]
				if file.endswith(tuple(imageFormats)):
					listFiles.append(file)
		return listFiles

	def on_done_filename(self, input): 
		if not self.image_url:
			self.image_url = imagefiles[input]
		
		print("gespeichert", self.image_url) 
		self.view.window().show_input_panel("Bildbeschreibung", "Bildbeschreibung hier einfuegen", self.on_done_img_description, None, None)                                               

	def on_done_img_description(self,input):
		self.desc = input
		print("self.image_url",self.image_url)
		print("self.desc",self.desc)

	def on_change(self, input):
		if input == -1:
			return

	def on_cancel(self, input):
		if input == -1:
			return



class Console():
	def __init__(self,view):
		return

	def printMessage(self,view, message):
		view.window().run_command("show_panel",{"panel": "console"});
		print("########BEGIN DEBUG-OUTPUT#########\n")
		print(message)
		print("\n########END DEBUG-OUTPUT#########")  



