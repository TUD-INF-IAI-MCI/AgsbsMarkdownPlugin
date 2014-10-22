# -*- coding: utf-8 -*-
import sublime, sublime_plugin
import os
import re
import codecs, re, sys
import collections
import json
import subprocess
import glob

"""
{ "keys": ["F2"], "command": "create_structure", "args": {"tag": ""} },
"""
class CreateStructureCommand(sublime_plugin.ApplicationCommand):
    def run(self):
        #sublime.active_window().show_input_panel("Titel und Kapitel/VL Anzahl eingeben", "Titel | Kapitelanzahl fuer ein Buch oder Thema der Vorlesungsfolie", self.on_done, self.on_change, self.on_cancel)        
        sublime.active_window().show_input_panel("Titel und Kapitel/VL Anzahl eingeben", "Titel | 2", self.on_done, self.on_change, self.on_cancel)        
    def on_done(self, input):
        str = input.split('|')
        folderDir = sublime.active_window().folders()[0]
        #current_driver = os.path(folderDir)[0]   
        currentDriver = folderDir.split(os.sep)[0]
        current_directory = folderDir.split(os.sep)[1]
        current_directory = os.sep.join(folderDir)              
        title = convertString(str[0])
        chapterNumber = str[1]           
        if (sys.platform.lower().find('win')== 0):
            # os is windows                                         
            command = "start cmd & cd "+folderDir+" & matuc new " +'\"'+title +'\" -c ' + chapterNumber \
                        +"& cd " +folderDir +os.sep +title +" & matuc conf -s " +'\"'+title +'\" update & exit'
        

        os.system(command)   
    
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

def convertString(input_string):
    
    replacements ={
        u'ä': 'ae',
        u'ü': 'ue',
        u'ö': 'oe',
        u'Ä': 'Ae',
        u'Ü': 'Ue',
        u'Ö': 'Oe',
        u'ß': 'ss',        
        '\s+': '_'
    }
    input_string = input_string.strip() 
    for key,value in replacements.items():
        input_string = re.sub(key,value,input_string,0)
    print input_string     
    return input_string

"""
count md files in path
"""
def count_md_file(path):
    count = 0
    for directoryname, directory_list, file_list in os.walk(path):
        for file in file_list:                        
            if file.endswith('.md'):
                count = count + 1
                
    return count

def findMarkdownFile(path):
    result =[]
    os.chdir(path)
    print "findMarkdownFile "
    for directoryname, directory_list, file_list in os.walk(path):

        print "file_list " +str(file_list)
        print "directoryname " +str(directoryname)
        print "directory_list " +str(directory_list)
        for file in file_list:
            if file.endswith(".md"):
                result.append(os.path.join(directoryname, file))
    return result

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
        # list ol, ul, code
        #elif tag in ['ul', 'ol', 'code']:
            #self.view.insert(edit, target, markdown_str)
        # blockqoute
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
        elif tag in ['table']:
            self.view.insert(edit, target, "| Tables        | Are           | Cool  | \n" 
            "| ------------- | ------------- | ----- |\n" 
            "| col 3 is      | right-aligned | $1600 |\n"
            "| col 2 is      | centered      |   $12 |\n"
            "| zebra stripes | are neat      |    $1 |\n")

class CmdCommand(sublime_plugin.TextCommand):
    def run(self, edit, function):        
        file_name=self.view.file_name()        
        osSeparator = ""
        command = ""
        if (sys.platform.lower().find('win')== 0):        
            osSeparator = "\\"
        else:
            osSeparator = os.sep    
        path = file_name.split(osSeparator)            
        current_driver = path[0]
        path.pop()    
        current_directory = osSeparator.join(path)

        path = self.view.file_name()        
        if function == "createHTML":
            if (sys.platform.lower().find('win')== 0):
            #command = "cd " +current_directory +"& " +current_driver +" & start cmd "                    
                command = "matuc conv " + file_name 
            elif (sys.platform.lower().find('linux')>= 0):
                print "createHTML"
                command = "gnome-terminal -e 'bash -c \"matuc conv "+ file_name +"\"'"                               
                print command
        elif function == "checkMarkdown":  
            if (sys.platform.lower().find('linux')>= 0):
                # os is  linux
                command = "gnome-terminal -e 'bash -c \"cd "+current_directory+"; matuc mk " +os.path.basename(path) + " > error.txt  \"'"                               
            elif (sys.platform.lower().find('wind')>= 0):
                # os is windows
                command = "cd " +current_directory +" & " +current_driver +" start cmd & matuc mk " +os.path.basename(path) + " > error.txt & exit"            
            elif (sys.platform.lower().find('darwin')>= 0):
                # os is os x - darwin
                print "not implemented yet"
        elif function == "checkMarkdown":              
            openFolders = self.view.window().folders()
            for folder in openFolders:
                md_files = findMarkdownFile(folder)
                files = os.walk
                if (sys.platform.lower().find('linux')>= 0):
                    # os is  linux                
                    command = "gnome-terminal -e 'bash -c \"cd "+current_directory+"; matuc mk " +os.path.basename(path) + " > error.txt  \"'"                                           
                elif (sys.platform.lower().find('win')== 0):
                    # os is windows  
                    print "folder " +str(current_directory)                          
                    command = "cd " +current_directory +" & " +current_driver +" start cmd & matuc mk " +'\"'\
                              +os.path.basename(path) + '\" > error.txt & exit'
                    #later 
                    #loc = '\"'+current_directory+'\"'                
                    #proc = subprocess.Popen(["matuc","mk", loc], shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                    #proc.wait()
                    #data = "\n".join(proc.communicate())                
                    #print data 
                elif (sys.platform.lower().find('darwin')>= 0):
                # os is os x - darwin
                    print "not implemented yet"                                 
        elif function == "createAll": 
            print "TODO createAll by Pressing F6"
            #command = "cd " +current_directory +"& " +current_driver +" start cmd & matuc mk " +file_name + " > error.txt"
        elif function == "showHTML":
            if (sys.platform.lower().find('linux')>= 0): 
                command = "gnome-terminal -e 'bash -c \"cd "+current_directory+"; "+file_name+ "\"'"                               
            if (sys.platform.lower().find('win')== 0):
                command = "cd " +current_directory +"& " +current_driver +" start cmd &" +file_name + "& exit"
        
        os.system(command)        

class InsertPanelCommand(sublime_plugin.TextCommand):    

    def run(self, edit, tag):        
        if tag == 'img':
            self.view.window().show_input_panel("Bild-URL", "Name der Bilddatei eintragen. z.b. bild.jpg", self.on_done_img_file, self.on_change, self.on_cancel)                               
        elif tag =='a':
            self.view.window().show_input_panel("Link-URL", "Link_eintragen", self.on_done_link, self.on_change, self.on_cancel)
        elif tag =='a name':
            self.view.window().show_input_panel("Ankername", "Anker_eintragen", self.on_done_anchor, self.on_change, self.on_cancel)
        elif tag =='page':
            self.view.window().show_input_panel("Seitenzahl", "", self.on_done_page, self.on_change, self.on_cancel)
    def on_done_page(self, input):
        #  if user cancels with Esc key, do nothing
        #  if canceled, index is returned as  -1
        if input == -1:
            return
       # if user picks from list, return the correct entry
        markdown = '||  Seite ' +input
        self.view.run_command(
            "insert_my_text", {"args":            
            {'text': markdown}})

    def on_done_img_file(self, input):
        self.pictureURL = input
        self.view.window().show_input_panel("Bildbeschreibung", "Bildbeschreibung hier einfuegen", self.on_done_img_description, self.on_change, self.on_cancel)                                               
#        markdown ='![ALternativtext](bilder/' +input +')'
       # markdown = '[Bildbeschreibung von ' +input +'](bilder.html#' + link +')'
 #       self.view.run_command(
  #          "insert_my_text", {"args":            
   #         {'text': markdown}})
    def on_done_img_description(self,description):
        #  if user cancels with Esc key, do nothing
        #  if canceled, index is returned as  -1        
        if description == -1:
            return


        if (len(description) >= 80):
            self.description_extern(description)
        else:
            # short description
            text = '!['+description+'](bilder/' +self.pictureURL +')'
            self.pictureURL + " " +description
            self.view.run_command("insert_my_text", {"args":            
                {'text': text}})        


    def description_extern(self, description):
        #  if user cancels with Esc key, do nothing
        #  if canceled, index is returned as  -1
        if description == -1:
            return
       # if user picks from list, return the correct entry
        
        """
            link to the alternativ description
        """
        link = "Bildbeschreibung von " +self.pictureURL
        heading_description = '\n\n## '+link
        link = link.lower().replace(" ","-")            
        markdown ='[![Beschreibung ausgelagert](bilder/' +self.pictureURL +')](bilder.html' +'#' +link +')'               
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
        with open(base +os.sep + 'bilder.md', 'r+') as fd:
            line_count = len(fd.readlines())
            # add heading_level_one
            if line_count <=0:
                fd.write(heading_level_one)               

            fd.write(heading_description)  
            fd.write("\n\n"+description) 
        

    def on_done_anchor(self, input):
        #  if user cancels with Esc key, do nothing
        #  if canceled, index is returned as  -1
        if input == -1:
            return
       # if user picks from list, return the correct entry
        markdown = '<a name=\"' +input +'\"></a>'
        self.view.run_command(
            "insert_my_text", {"args":            
            {'text': markdown}})

    def on_done_link(self, input):
        #  if user cancels with Esc key, do nothing
        #  if canceled, index is returned as  -1
        if input == -1:
            return
       # if user picks from list, return the correct entry
        markdown = '[Linktext aendern](' +input +')'
        self.view.run_command(
            "insert_my_text", {"args":            
            {'text': markdown}})

    def on_change(self, input):
          if input == -1:
            return

    def on_cancel(self, input):
        if input == -1:
            return

class Move_caret_topCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        screenful = self.view.visible_region()

        col = self.view.rowcol(self.view.sel()[0].begin())[1]
        row = self.view.rowcol(screenful.a)[0] + 1
        target = self.view.text_point(row, col)

        self.view.sel().clear()
        self.view.sel().add(sublime.Region(target))
    def on_done(self, input):
 
        #  if user cancels with Esc key, do nothing
        #  if canceled, index is returned as  -1
        if input == -1:
            return

 
        # if user picks from list, return the correct entry
        image_markdown = '![Alternativtext]  (' +input +')'
        self.view.run_command(
            "insert_my_text", {"args":            
            {'text': image_markdown}})

    def on_change(self, input):
          if input == -1:
            return
    def on_cancel(self, input):
        if input == -1:
            return

class InsertMyText(sublime_plugin.TextCommand):
 
    def run(self, edit, args):
 
        # add this to insert at current cursor position
        # http://www.sublimetext.com/forum/viewtopic.php?f=6&t=11509
 
        self.view.insert(edit, self.view.sel()[0].begin(), args['text'])


class Move_caret_middleCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        screenful = self.view.visible_region()

        col = self.view.rowcol(self.view.sel()[0].begin())[1]
        row_a = self.view.rowcol(screenful.a)[0]
        row_b = self.view.rowcol(screenful.b)[0]

        middle_row = (row_a + row_b) / 2
        target = self.view.text_point(middle_row, col)

        self.view.sel().clear()
        self.view.sel().add(sublime.Region(target))

class Move_caret_bottomCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        screenful = self.view.visible_region()

        col = self.view.rowcol(self.view.sel()[0].begin())[1]
        row = self.view.rowcol(screenful.b)[0] - 1
        target = self.view.text_point(row, col)

        self.view.sel().clear()
        self.view.sel().add(sublime.Region(target))

class Move_caret_forwardCommand(sublime_plugin.TextCommand):
    def run(self, edit, nlines):
        screenful = self.view.visible_region()

        (row,col) = self.view.rowcol(self.view.sel()[0].begin())
        target = self.view.text_point(row+nlines, col)

        self.view.sel().clear()
        self.view.sel().add(sublime.Region(target))
        self.view.show(target)

class Move_caret_backCommand(sublime_plugin.TextCommand):
    def run(self, edit, nlines):
        screenful = self.view.visible_region()

        (row,col) = self.view.rowcol(self.view.sel()[0].begin())
        target = self.view.text_point(row-nlines, col)

        self.view.sel().clear()
        self.view.sel().add(sublime.Region(target))
        self.view.show(target)


"""
 Erweiterung basierend auf Sebastians Code
 fuehrt sebastians erweiterung aus und speichert inhalt in inhalt.md ab
"""
class CreateTocFileCommand(sublime_plugin.ApplicationCommand):
    def run(self):
        base = sublime.windows()[0].folders()[0] 
    
        c = create_index(base)
        c.walk()        
        index = c.get_index()
        md_index = index2markdown_TOC(index)
        WriteIndex2File(base,md_index.get_markdown_page())

#erfordert datei
# class CreateTocCommand(sublime_plugin.TextCommand):
#     def run(self, edit):
#         path = self.view.file_name()
#         base = os.path.split(path)[0]
#         self.__dir = base

#         # for root, dirs, files in os.walk(base):
#         #     for folder in dirs:
#         #         print folder
#         # collect_all_md_files(base)   
#         #test_file_walk()
#         c = create_index(base)
#         c.walk()
#         index = c.get_index()
#         md_index = index2markdown_TOC(index)
#         WriteIndex2File(base,md_index.get_markdown_page())        
#         # window.run_command("save")
#         # window.run_command("reload")


class SaveAndReloadCommand(sublime_plugin.WindowCommand):
    def run(self):                        
        self.window.run_command("reload_view")
        
        


       
def WriteIndex2File(base,content):

    indexFile = base + os.sep + "index.md"
    print "Save 2 file " +indexFile
    fd = os.open(indexFile, os.O_RDWR|os.O_CREAT)
    text = content.encode('utf-8').strip()
    os.write(fd, text)
    os.close(fd)


def test_markdown_parser():
    m = markdownParser("Heya\n====\n\nImportant advisories\n---------\n\n\n###### - Seite 6 -\n")
    m.parse()
    for item in m.get_data():
        print(repr(item))
    print("Done.")

def test_file_walk():    
    c = create_index('.')
    c.walk()
    for key, value in c.get_index().items():
        print(key+repr(value)+'\n\n')
    return c.get_index()

# -- if not imported but run as main module, test functionality --

def test_index2markdown_TOC():
   # print "test_index2markdown_TOC"
    idx = test_file_walk()
    c = index2markdown_TOC(idx, 'de')
    #print(c.get_markdown_page())

if __name__ == '__main__':
    #test_markdown_parser()
    #test_file_walk()
    test_index2markdown_TOC()

