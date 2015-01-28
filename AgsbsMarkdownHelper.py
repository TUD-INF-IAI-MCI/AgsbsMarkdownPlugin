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
console = Console(None)


global messageBox
messageBox = MessageBox()
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
{ "keys": ["alt+shift+l"], "command": "insert_panel", "args": {"tag": "a"} }
"""
class InsertPanelCommand(sublime_plugin.TextCommand):   
	def run(self, edit, tag):		
		if tag == "img":
			# add content to dictionary
			self.image_url =""			
			if(settings.get("hints")):				
				messageBox.showMessageBox("Sie wollen ein Bild hinzufügen. Es sind 2 Eingaben erforderlich: \n"
					"\t1. Speicherort des Bildes \n"
					"\t2. Alternativbeschreibung zum Bild \n")
			imageFormats = settings.get("image_formats")
			global imagefiles
			imagefiles = self.getFileName(imageFormats)
			self.show_prompt(imagefiles,tag)
		elif tag =="a":
			if(settings.get("hints")):
				messageBox.showMessageBox("Sie wollen ein Link hinzufügen. Es sind 2 Eingaben erforderlich: \n"
					"\t1. Linktext, z.B. Webseite der TU Dresden \n"
					"\t2. URL, http://www.tu-dresden.de  \n")
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

"""
{ "keys": ["alt+shift+t"], "command": "insert_table"}
"""
class InsertTableCommand(sublime_plugin.TextCommand):
	def run(self, edit):
		sublime.active_window().show_input_panel("Spalten|Zeilen", "Spalten|Zeilen", self.on_done, self.on_change, self.on_cancel)
	def on_done(self, input):
		self.createTable(input)
	def on_change(self, input):
        #  if user cancels with Esc key, do nothing
        #  if canceled, index is returned as  -1
		if input == -1:
			return
	def on_cancel(self, input):
        #  if user cancels with Esc key, do nothing
        #  if canceled, index is returned as  -1
		if input == -1:
			return
	def createTable(self, input):
		try:
			cols = int(input.split("|")[0])
			rows = int(input.split("|")[1])
		except ValueError:
			messageBox.showMessageBox("Geben Sie die Spalten und Zeilen getrennt mit einem \"|\" an. \n"
				"Zum Beispiel für eine Tabelle mit 3 Spalten und 5 Reihen geben Sie \n"
				"3|5 ein!")
			return
		
		#if(	settings.get("table_default_values"))
		markdown =""
		for r in range(0,rows):
			markdown += "|"
			for c in range(0,cols): 
				cellValue = ""
				if(	settings.get("table_default_values")):
					cn = c + 1 #colnumber
					rn = r + 1 #rownumber
					print("#######rn",r)
					cellValue = "Wert für Spalte %d und Zeile %d" % (cn,rn)
				markdown += cellValue + "|"
			if(r == 0): 
				markdown += "\n" # line break
				markdown += "|"	
				for c in range(0,cols):
					markdown += "----------|"
			# add separator
			markdown += "\n" # line break for next row
		markdown += "\n" # final line break		
		if(Debug):
			message = "Table with \n\t %d columns\n\t %d rows \n" % (cols, rows)
			message += "Generated markdown is \n" +markdown
			console.printMessage(self.view, message)		
		# insert markdown
		self.view.run_command("insert_my_text", {"args":{'text': markdown}})

class AddTagCommand(sublime_plugin.TextCommand):
     def run(self, edit, tag, markdown_str):
        screenful = self.view.visible_region()
        (row,col) = self.view.rowcol(self.view.sel()[0].begin())
        target = self.view.text_point(row, 0)
        # strong and em
        if tag in ['em', 'strong']:                
                (row,col) = self.view.rowcol(self.view.sel()[0].begin()) 
                for region in self.view.sel():
                    if not region.empty():
                        selString = self.view.substr(region)                       
                        word = self.view.word(target)                                               
                        movecursor = len(word)   
                        diff = 0
                        if movecursor > 0:
                            diff = movecursor/2        
                        strg = str(diff)
                    
                        target = self.view.text_point(row, diff)
                        self.view.sel().clear() 
                        if region.a < region.b:
                            firstPos =  region.a
                            endPos = region.b
                        else:
                            firstPos =  region.b    
                            endPos = region.a                           
                        endPos = endPos + len(markdown_str)                        
                        self.view.insert(edit,firstPos,markdown_str)                        
                        self.view.insert(edit,endPos,markdown_str)
        #heading
        elif tag in ['h']:
              for region in self.view.sel():
                    if not region.empty():
                        firstPos = 0
                        if region.a < region.b:
                            firstPos =  region.a
                        else:
                            firstPos =  region.b
                        self.view.insert(edit,firstPos,markdown_str)               
        elif tag in ['blockqoute', 'ul', 'ol', 'code']:
            for region in self.view.sel():
                    if not region.empty():
                        lines = self.view.split_by_newlines(region)
                        for i,line in enumerate(lines):
                            if tag == 'ol':
                                number = 1 +i                                     
                                self.view.insert(edit, line.a+3*i, str(number)+'. ')                                
                            else:                                            
                                self.view.insert(edit, line.a+2*i, markdown_str)

        elif tag in ['hr']:
            self.view.insert(edit, target, markdown_str +"\n")
     
#
# Below this are only helpers
#

class InsertMyText(sublime_plugin.TextCommand):
	def run(self, edit, args):
		self.view.insert(edit, self.view.sel()[0].begin(), args['text'])

class MessageBox():
	def __init__(self):
		return
	def showMessageBox(self,message):
		sublime.message_dialog(message)

class Console():
	def __init__(self,view):
		return

	def printMessage(self,view, message):
		view.window().run_command("show_panel",{"panel": "console"});
		print("########BEGIN DEBUG-OUTPUT#########\n")
		print(message)
		print("\n########END DEBUG-OUTPUT#########")  



