from __future__ import print_function
import sublime, sublime_plugin
import sys
import os
import re
import codecs, re, sys
import collections
import webbrowser 

VERSION = int(sublime.version())

reloader = "reloader"

if VERSION > 3000:
	print("sublime version is higher >= 3")	
	from .agsbs_infrastructure.MAGSBS import master
	from .agsbs_infrastructure.MAGSBS import config as config
	from .agsbs_infrastructure.MAGSBS.quality_assurance import mistkerl as mistkerl
	from .agsbs_infrastructure.MAGSBS import pandoc
	from .agsbs_infrastructure.MAGSBS import filesystem
	#from .agsbs_infrastructure.MAGSBS import .errors
	#from .agsbs_infrastructure.MAGSBS.filesystem import *
	#from .agsbs_infrastructure.MAGSBS.mparser import *
	#from .agsbs_infrastructure.MAGSBS.errors import *
	#from .agsbs_infrastructure.MAGSBS.pandocfilters import *
	
	#from .MAGSBS.config import *
	
	#from .MAGSBS.matuc import *
	#from .MAGSBS.lib.enum import *
	
else: 
	print("sublime version  < 3")
	from MAGSBS import reloader
	from MAGSBS.master import *

# Make sure all dependencies are reloaded on upgrade
if reloader in sys.modules:
    reload(sys.modules[reloader])



#
# Below this are only helpers
#

class Browser():
	def __init__(self,filename):
		url = "file://"+filename	
		webbrowser.open(url,new = 2)


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



settings = sublime.load_settings("Agsbshelper.sublime-settings")
global Debug
Debug = settings.get("debug")	
global autoload_html
autoload_html = settings.get("autoload_html")
global messageBox
messageBox = MessageBox()
global console
console = Console(None)


"""
{ "keys": ["F2"], "command": "create_structure", "args": {"tag": ""} }
"""
class CreateStructureCommand(sublime_plugin.TextCommand):
    def run(self,edit):
    	self.view.window().show_input_panel("Struktur anlegen", "title|kapitel|sprache|vorwort", self.one_done, None, self.on_cancel)	
    def one_done(self, input):
    	inputs = input.split("|")    	    
    	path = sublime.active_window().folders()[0]
    	os.chdir(path)
    	preface = bool(inputs[3])
    	builder = filesystem.init_lecture(inputs[0],int(inputs[1]),lang=inputs[2])
    	builder.set_has_preface(preface)
    	builder.generate_structure()
    	if(Debug):
    		console = Console(self.view)
    		console.printMessage(self.view,path)    		
    def on_cancel(self, input):
    	print(input)
    	if input == -1:
    		return

"""
{ "keys": ["f5"], "command": "cmd", "args": {"function": "create_html_file"} }
"""

class CreateHtmlFileCommand(sublime_plugin.TextCommand):
    def run(self,edit):
        file_name = self.view.window().active_view().file_name()
        path = os.path.dirname(self.view.window().active_view().file_name())
        #file_name = file_name.encode('ascii', 'strict')
        #file_name = file_name.replace("\\","\\\\")
        file_name = str(file_name)
        print(file_name)
        os.chdir(path)
        p = pandoc.pandoc()
        p.convert(file_name)
        if(autoload_html):        	
        	Browser(file_name.replace(".md",".html"))

"""
{ "keys": ["f6"], "command": "cmd", "args": {"function": "createAll"} } 
"""
class CreateAllCommand(sublime_plugin.TextCommand):
    def run(self,edit):
        path = os.path.dirname(self.view.window().active_view().file_name())
        print("#####################")
        parent = os.path.abspath(os.path.join(path, os.pardir))
        print(path)
        os.chdir(path)
        p = pandoc.pandoc()
        m = master.Master(parent)
        m.run()
        if(autoload_html):        	
        	parent = os.path.join(parent,"inhalt.html")
        	print(parent)
        	Browser(parent)

"""
{ "keys": ["f3"], "command": "cmd" , "args": {"function": "checkAll"} }
"""
class CheckAllCommand(sublime_plugin.TextCommand):
    def run(self, edit):         	
    	path = os.path.dirname(self.view.window().active_view().file_name())
    	mk = mistkerl.MistKerl()
    	errors = mk.run(path)
    	if(Debug):    		
    		print(errors)
    		console.printMessage(self.view,"check with MK")

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
			if imagefiles:
				self.show_prompt(imagefiles,tag)
			else:
				dirname = os.path.dirname(self.view.file_name())
				dirname = os.path.join(dirname,"bilder")
				message = "Im Ordner Bilder sind keine Bilddaten gespeichert.\n"
				message += "Speichern zuerst Bilder in dem Ordner\n"
				message += dirname +"\n"
				message += "um ein Bild einfügen zu können." 
				sublime.error_message(message)	
		elif tag =="a":
			if(settings.get("hints")):
				messageBox.showMessageBox("Sie wollen ein Link hinzufügen. Es sind 2 Eingaben erforderlich: \n"
					"\t1. Linktext, z.B. Webseite der TU Dresden \n"
					"\t2. URL, http://www.tu-dresden.de  \n")					
			self.show_prompt(None,tag)
	def show_prompt(self, listFile,tag):
		if tag == "img":
			self.view.window().show_quick_panel(listFile,self.on_done_filename,sublime.MONOSPACE_FONT)
		elif tag == "a":
			self.view.window().show_input_panel("Linktext", "", self.one_done_linktext, self.on_change, self.on_cancel)

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

	def one_done_linktext(self,input):
		if input == -1 or not input:			
			sublime.error_message("Linktext darf nicht leer sein")			
			return
		else:			
			self.linktext = input
		self.view.window().show_input_panel("URL", "", self.on_done_url, self.on_change, self.on_cancel)

	def on_done_url(self, input):
        #  if user cancels with Esc key, do nothing
        #  if canceled, index is returned as  -1
		if input == -1 or not input:
			sublime.error_message("URL darf nicht leer sein")
			return       
		#markdown = '[Linktext aendern](' +input +')'
		if(not input.lower().startswith("http://") or not input.lower().startswith("https://")):
			input = "http://"+input
		markdown = "[%s](%s)" % (self.linktext,input.lower())
		self.view.run_command(
			"insert_my_text", {"args":            
            {'text': markdown}})

	def on_done_filename(self, input): 				
		if input == -1 and not self.image_url:  # esc
			sublime.error_message("Wählen Sie eine Bilddatei aus!")			
		elif input != -1 :
			self.image_url = imagefiles[input]					
			self.view.window().show_input_panel("Bildbeschreibung", "Bildbeschreibung hier einfügen", self.on_done_img_description, None, None)                                               


	def on_done_img_description(self,description):
		self.desc = description
		default_desc = "Bildbeschreibung hier einfügen"
		print(description)		
		if description == -1:
			sublime.error_message("Fehler in on_done_img_description")
		elif description == default_desc:			
			sublime.error_message("Sie haben die Standardbildbeschreibung nicht geändert!")			
		else: 
			if(len(description)>=80):
				self.description_extern(description)
			else:
				text = '!['+description+'](bilder/' +self.image_url +')'
				#self.image_url + " " +description
				if(Debug):
					message = "image short \n" +text
					console.printMessage(self.view,message)
				self.view.run_command("insert_my_text", {"args":{'text': text}})
	
	def description_extern(self,description):
		"""
            link to the alternativ description
        """
		link = "Bildbeschreibung von " +self.image_url
		heading_description = '\n\n## '+link
		link = link.lower().replace(" ","-")            
		markdown ='[![Beschreibung ausgelagert](bilder/' +self.image_url +')](bilder.html' +'#' +link +')'               
		self.view.run_command(
            "insert_my_text", {"args":            
            {'text': markdown}})
		path = self.view.file_name()
		base = os.path.split(path)[0]
		"""
            try to load bilder.md file or create
        """
        #fd = os.open(base +os.sep + 'bilder.md', os.O_RDWR|os.O_CREAT)
        #print fd.readlines()
        #count =  fd.read
		fd = os.open(base +os.sep + 'bilder.md', os.O_RDWR|os.O_CREAT)
		os.close(fd)
		heading_level_one = '# Bilderbeschreibungen \n \n'
		heading_level_one = heading_level_one.encode('utf-8').strip()
		with codecs.open(base +os.sep + 'bilder.md', "r+", encoding="utf8") as fd:
			line_count = len(fd.readlines())
			if line_count <=0:
				fd.write(heading_level_one)
		with codecs.open(base +os.sep + 'bilder.md', "a+", encoding="utf8") as fd:            
			fd.write(heading_description)		
			fd.write("\n\n"+description) 


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
"""
{ "keys": ["alt+shift+h"], "command": "add_tag", "args": {"tag": "h", "markdown_str":"#"} }
{ "keys": ["alt+shift+i"], "command": "add_tag", "args": {"tag": "em", "markdown_str":"_"} }
{ "keys": ["alt+shift+r"], "command": "add_tag", "args": {"tag": "hr", "markdown_str":"----------"}}
"""
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
     



