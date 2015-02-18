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
	from .agsbs_infrastructure.MAGSBS.quality_assurance import meta as meta
	from .agsbs_infrastructure.MAGSBS import factories
	#from .agsbs_infrastructure.MAGSBS import .errors
	#from .agsbs_infrastructure.MAGSBS.filesystem import *
	#from .agsbs_infrastructure.MAGSBS.mparser import *
	#from .agsbs_infrastructure.MAGSBS.errors import *
	#from .agsbs_infrastructure.MAGSBS.pandocfilters import *
	
	#from .MAGSBS.config import *
	
	#from .MAGSBS.matuc import *
	#from .MAGSBS.lib.enum import *
	
else: 
	sublime.error_message("sublime version  < 3; not supported")
	

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
	def printMessage(self,view, category,  message):		
		view.window().run_command("show_panel",{"panel": "console"})
		print("######## Begin",category," #########\n")
		print(message)
		print("\n######## END ",category," #########")  

class Saver(): # ToDo: function
	def saveAllDirty(self):			
		for w in sublime.windows():
			for v in w.views():
				if not v.file_name():
					dirty_unname = True
					# maybe toDo 					
				elif v.file_name().endswith(".md"):
					if v.is_dirty():						
						if settings.get("autosave"):
							v.run_command("save")
						else:			
							sublime.error_message("Es gibt ungespeicherte md-Dateien. Daher kann könnten die generierten Dateien\n"
													 "Fehler enthalten. Aktivieren Sie autosave in der Konfigurationsdatei")
							return
						
settings = sublime.load_settings("Agsbshelper.sublime-settings")
global Debug
Debug = settings.get("debug")	
global autoload_html
autoload_html = settings.get("autoload_html")
global messageBox
messageBox = MessageBox()
global console
console = Console()
global saver
saver = Saver()

class CreateStructureCommand(sublime_plugin.TextCommand):
	"""
{ "keys": ["F2"], "command": "create_structure", "args": {"tag": ""} }
	"""
	def run(self,edit):
		self.view.window().show_input_panel("Struktur anlegen",
				"title|kapitel|sprache|vorwort", self.one_done, None,
				self.on_cancel)

	def one_done(self, input):
		inputs = input.split("|")    	    
		path = sublime.active_window().folders()[0]
		os.chdir(path)
		preface = bool(int(inputs[3]))
		# init_lecture(title, section_number,language)		
		builder = filesystem.init_lecture(inputs[0], int(inputs[1]),
				lang=inputs[2])
		if not preface:		
			print("KEIN vorwort",inputs[3])
		else:			
			print("+++vorwort",inputs[3])
		builder.set_has_preface(preface)
		builder.generate_structure()
		if(Debug):
			console = Console()
			console.printMessage(self.view,'Debug',path)			

	def on_cancel(self, input):
		print(input)
		if input == -1:
			return

class CheckWithMkCommand(sublime_plugin.TextCommand):
	"""
{ "keys": ["f3"], "command": "check_with_mk" , "args": {"function": "checkFile"} }
{ "keys": ["f4"], "command": "check_with_mk" , "args": {"function": "checkAll"} }
	"""
	def run(self, edit, function): 
		try:
			file_name = self.view.window().active_view().file_name()
			if not file_name:
					sublime.error_message("Öffnen Sie eine Markdown-Datei um die \nÜberprüfung mit MK zu starten!")		
					return
			else:
				path = os.path.dirname(self.view.window().active_view().file_name())
		except OSError:
			sublime.error_message("Öffnen Sie eine Markdown-Datei um die Convertierung zu starten")
			return
		parent = os.path.abspath(os.path.join(path, os.pardir))   
		mk = mistkerl.Mistkerl()
		message = ""
		errors = ""						
		if function =="checkFile":
			errors = mk.run(path)
		elif function =="checkAll":
			errors = mk.run(parent)			
		if(len(errors) ==0):
			console.printMessage(self.view,'Error',"Nun denn, ich konnte keine Fehler entdecken. Hoffen wir, dass es auch wirklich\nkeine gibt ;-).")
		else:
			sublime.error_message("MK hat Fehler gefunden, weiteren Information \nfinden sie in auf der Console.")
			formatter = meta.error_formatter()
			formatter.set_itemize_sign("  ")
			console.printMessage(self.view,'MK Error', formatter.format_errors(errors))
		if(Debug):			
			if function == "checkFile":
				message = "check file " + self.view.window().active_view().file_name() +" with MK"
			elif function == "checkAll":
				message = "check path " + parent +" with MK"
			console.printMessage(self.view,'Debug '+function, message)

class CreateHtmlFileCommand(sublime_plugin.TextCommand):
	"""
{ "keys": ["f5"], "command": "cmd", "args": {"function": "create_html_file"} }
	"""

	def run(self,edit):
		saver.saveAllDirty()
		try:
			file_name = self.view.window().active_view().file_name()
			path = os.path.dirname(self.view.window().active_view().file_name())
		except OSError:
			sublime.error_message("Öffnen Sie eine Markdown-Datei um die Convertierung zu starten")    	
			return    		    	
		os.chdir(path)		
		p = pandoc.pandoc()		
		p.convert(file_name)
		if(autoload_html):
			print("open in Browser")
			Browser(file_name.replace(".md",".html"))

class CreateAllCommand(sublime_plugin.TextCommand):
	"""
{ "keys": ["f6"], "command": "cmd", "args": {"function": "createAll"} } 
	"""
	def run(self,edit):
		saver.saveAllDirty()
		try:
			path = os.path.dirname(self.view.window().active_view().file_name())
		except OSError:
			sublime.error_message("Öffnen Sie eine Markdown-Datei um die Convertierung zu starten")
			return
		parent = os.path.abspath(os.path.join(path, os.pardir))        
		os.chdir(path)
		m = master.Master(parent)
		m.run()
		if(autoload_html):
			parent = os.path.join(parent,"inhalt.html")
			print("open ", parent)
			Browser(parent)



class InsertPanelCommand(sublime_plugin.TextCommand):   
	"""
{ "keys": ["ctrl+alt+i"], "command": "insert_panel", "args": {"tag": "img"}},
{ "keys": ["alt+shift+l"], "command": "insert_panel", "args": {"tag": "a"} }
	"""
	def run(self, edit, tag):		
		if tag == "img":			
			# add content to dictionary
			self.image_url =""			
			global imagefiles
			imageFormats = settings.get("image_formats")	
			imagefiles = self.getFileName(imageFormats)
			if imagefiles:				
				if(settings.get("hints")):				
					messageBox.showMessageBox("Sie wollen ein Bild hinzufügen. Es sind 2 Eingaben erforderlich: \n"
					"\t1. Speicherort des Bildes \n"
					"\t2. Alternativbeschreibung zum Bild \n")
				self.show_prompt(imagefiles,tag)
			else:
				dirname = os.path.dirname(self.view.file_name())
				dirname = os.path.join(dirname,"bilder")
				message = "Im Ordner Bilder sind keine Bilddaten gespeichert.\n"
				message += "Speichern zuerst Bilder in dem Ordner\n"
				message += dirname +"\n"
				message += "um ein Bild einfügen zu können." 
				sublime.error_message(message)
				return		
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
		for (dirname,dirs, files) in os.walk(dir):					
			for file in files:				
				if file.endswith(tuple(imageFormats)):
					parentname = os.path.basename(os.path.normpath(dirname))
					listFiles.append(parentname +"/" + file)
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
		message = ""
		img_desc = factories.ImageDescription(self.image_url)
		if img_desc.img_maxlength > len(description):
			img_desc.set_outsource_descriptions(False)
		else:
			img_desc.set_outsource_descriptions(True)
		img_desc.set_description(description)
		img_desc.set_title("title_default")				
		img_output = img_desc.get_output();

		
		if(len(img_output)==1):			
			self.writeMd(img_output[0])
		else:	
			self.writeMd(img_output[0])
			self.description_extern(img_output[1])
		if(Debug):			
			console.printMessage(self.view, "Debug image", message)

	def writeMd(self,markdown_str):
		self.view.run_command("insert_my_text", {"args":{'text': markdown_str}})

	def description_extern(self,description):
		path = self.view.file_name()
		base = os.path.split(path)[0]
		"""
			try to load bilder.md file or create
		"""		
		fd = os.open(base +os.sep + 'bilder.md', os.O_RDWR|os.O_CREAT)
		os.close(fd)
		heading_level_one = '# Bilderbeschreibungen \n\n'		
		with codecs.open(base +os.sep + 'bilder.md', "r+", encoding="utf-8") as fd:
			if len(fd.readlines()) <=0:
				fd.write(heading_level_one)
		with codecs.open(base +os.sep + 'bilder.md', "a+", encoding="utf-8") as fd:            						
			fd.write(description) 


	def on_change(self, input):
		if input == -1:
			return

	def on_cancel(self, input):
		if input == -1:
			return


class InsertPageCommand(sublime_plugin.TextCommand):
	"""
 { "keys": ["alt+shift+p"], "command": "insert_page"}
	"""   
	def  run(self, edit):
		self.view.window().show_input_panel("Seitenzahl", "", self.on_done_page, None,None)
	def on_done_page(self, input):    
		if input == -1:
			return       
		markdown = '||  - Seite ' +input + ' -'
		self.view.run_command("insert_my_text", {"args":{'text': markdown}})

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
			console.printMessage(self.view, "Debug", message)		
		# insert markdown
		self.view.run_command("insert_my_text", {"args":{'text': markdown}})

class AddTagCommand(sublime_plugin.TextCommand):
	"""
{ "keys": ["alt+shift+h"], "command": "add_tag", "args": {"tag": "h", "markdown_str":"#"} }
{ "keys": ["alt+shift+i"], "command": "add_tag", "args": {"tag": "em", "markdown_str":"_"} }
{ "keys": ["alt+shift+r"], "command": "add_tag", "args": {"tag": "hr", "markdown_str":"----------"}}
	"""
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
	 



