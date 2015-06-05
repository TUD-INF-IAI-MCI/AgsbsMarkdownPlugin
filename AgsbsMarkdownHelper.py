from __future__ import print_function
import sublime
import sublime_plugin
import sys
import os
import re
import codecs
import collections
import webbrowser
import csv


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

    if(sys.platform.lower().startswith("win")):
        user_paths = os.environ['PATH'].split(os.pathsep)
        indices = [i for i, elem in enumerate(user_paths) if 'matuc' in elem]
        if not indices:
            sublime.error_message("Installieren Sie das Programm Matuc. Weitere Informationen\n finden Sie unter"
            " http://elvis.inf.tu-dresden.de/wiki/index.php/Matuc.\n"
            "Oder passen Sie die PATH-Angabe an, falls Sie das Programm Matuc installiert haben.")
        else:
            newPath = user_paths[indices[0]] +os.sep+ "binary"
            if not newPath in os.environ['PATH']:
                os.environ['PATH'] +=";"+user_paths[indices[0]] +os.sep+ "binary"
    elif sys.platform.lower().startswith("darwin"):
        os.environ['PATH'] += ":/opt/local/bin"
        print("'PATH'",os.environ['PATH'])
else:
    sublime.error_message("sublime version  < 3; not supported")

def plugin_loaded():
    global settings

    settings = sublime.load_settings('Agsbs Markdown Helper.sublime-settings')
    sublime.save_settings('Agsbs Markdown Helper.sublime-settings')
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

class Bunch(object):

    def __init__(self, **kwds):
        self.__dict__.update(kwds)

    def __eq__(self, other):
        return self.__dict__ == other.__dict__

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

class CreateInternalLink(sublime_plugin.TextCommand):
    """
    { "keys": ["crtl+shift+l"], "command": "create_internal_link"}
    """
    def run(self,edit):
        self.linkDic = {}
        file_name = self.view.window().active_view().file_name()
        if file_name and file_name.lower().endswith(".md"):
            saver.saveAllDirty()
            path = os.path.dirname(file_name)
            parent = os.path.abspath(os.path.join(path, os.pardir))
            for root, dirs, files in os.walk(str(parent)):
                for file in files:
                    if file.endswith(".md"):
                            with codecs.open(os.path.join(root,file),'r',encoding='utf8') as md_file:
                                # reg = re.compile(r"\R[#]{1,6}[ \d\w.-®-]+\R")   # regex \R[#]{1,6}[ \d\w.-®-]+\R
                                content = md_file.read()
                                # remove navigation to pages and slides
                                content = re.sub("(Seiten|Folien|Pages|Slides)[\[\]\(\):\s\d#\w-]*","",content)
                                regex = re.compile('[\w\d#~& "\-\?\+@\!\.\,\(\)\[\]\{\}\'$§%\*\_\;\:]+\n[=]+|\W[#]{1,6}[\w\d#~& "\-\?\+@\!\.\,\(\)\[\]\{\}\'$§%\*\_\;\:]+\n')
                                headings = re.findall(regex, content)
                                if headings:
                                    parent = os.path.split(os.path.dirname(md_file.name))[1]
                                    self.linkDic[parent+'/'+file] = headings
            self.show_link_quick_panel(self.linkDic)
        else:
            sublime.error_message("Selektieren Sie eine Markdown-Datei um einen \ninternen Link einzufügen.")

    def show_link_quick_panel(self, linkDic):
        self.view.window().show_quick_panel(self.createLinkList(linkDic), self.on_done, sublime.MONOSPACE_FONT)

    def createLinkList(self, linkDic):
        self.linkList = []
        for entry in linkDic:
            for listEntry in linkDic[entry]:
                headingStr = re.sub(r'[#]{1,6}|[=]+', r'', ''.join(listEntry))
                headingStr = re.sub(r'^\s+', r'', headingStr)  # trailing white space
                self.linkList.append(entry + "|" + headingStr)
        self.linkList.sort()
        return self.linkList

    def on_done(self, input):
        if input != -1:     # -1 = esc
            values = self.linkList[input].split('|')
            anchor = re.sub('[#~&"\?\+@\!\,\[\]\(\)\{\}\'$§%\*\_\;\:)=`´/]*',"",values[1].lower())
            anchor = re.sub("\s","-",anchor)
            markdown = "[%s](%s)" % (values[1].replace('\n', ''), "../" + values[0].lower().replace(".md", ".html") + "#" + anchor)
            self.view.run_command("insert_my_text", {"args": {'text': markdown}})


class AddFolderToProject(sublime_plugin.TextCommand):
    """
    { "keys": ["shift+f2"], "command": "add_folder_to_project"}
    """
    def run(self, edit):
        sublime.active_window().run_command('prompt_add_folder')


class CreateStructureCommand(sublime_plugin.TextCommand):
    """
{ "keys": ["f2"], "command": "create_structure", "args": {"tag": ""} }
    """
    def run(self,edit):
        self.counter = 0
        self.keys = ['title', 'chapter_count', 'language', 'preface']
        self.dictionary ={
            'title': Bunch(name='Titel', value=''),
            'chapter_count': Bunch(name='Kapitel', value=''),
            'language': Bunch(name='Sprache', value=''),
            'preface': Bunch(name='Vorwort', value=''),
        }
        if sublime.active_window().folders():
            pass
        else:
            message = u"Sie müssen ein Projekt anlegen und einen Ordner auswählen,\n"
            message += u"um die Buchstruktur anlegen zu können."
            sublime.error_message(message)
            return
        if(settings.get("hints")):
            messageBox.showMessageBox("Zum Anlegen der Struktur geben Sie bitte folgende Werte ein: \n"
                "\tTitel = Buch oder Lehrmaterial-Name\n"
                "\tKapitelanzahl = erlaubte Werte sind ganze Zahlen\n"
                "\tSprache = erlaubte Werte sind de oder en \n"
                "\tVorwort = erlaubte Werte sind ja oder nein")
        self.show_prompt()
    def show_prompt(self):
        self.view.window().show_input_panel(self.dictionary[self.keys[self.counter]].name, '', self.on_done, None, None)

    def on_done(self, input):
        value = self.check_user_input(self.keys[self.counter], input)
        if value is not None:
            self.dictionary[self.keys[self.counter]].value = value
            self.counter += 1
        if self.counter < (len(self.dictionary)):
            self.show_prompt()
        else:
            self.input_done()

    def input_done(self):
        path = sublime.active_window().folders()[0]

        cwd = os.getcwd()
        os.chdir(path)
        builder = filesystem.init_lecture(self.dictionary['title'].value, self.dictionary['chapter_count'].value,
                lang=self.dictionary['language'].value)
        builder.set_has_preface(self.dictionary['preface'].value)
        builder.generate_structure()
        if(Debug):
            console = Console()
            console.printMessage(self.view,'Debug',path)
        os.chdir(cwd)
    def check_user_input(self, key, content):
        error = False
        if key == 'title':
            error =  False
        if key == 'chapter_count':
            try:
                content = int(content)
                error =  False
            except ValueError:
                error =  True
                messageBox.showMessageBox("Kapitelanzahl muss eine Zahl sein!")
        elif key == 'language':
            if not content in ['de','en']:
                error =  True
                messageBox.showMessageBox("Zulässige Werte für die Sprache sind nur \"de\" und \"en\"")
        elif key == 'preface':
            if not content in ['ja','nein']:
                messageBox.showMessageBox("Zulässige Werte für das Vorwort sind nur \"ja\" und \"nein\"")
                error =  True
            else:
                content = True if content.lower() in "ja" else False
        if not error:
            return content
        else:
            self.counter = self.keys.index(key)
            return None

    def on_cancel(self, input):
        if input == -1:
            return

class CheckWithMkCommand(sublime_plugin.TextCommand):
    """
{ "keys": ["f3"], "command": "check_with_mk" , "args": {"function": "checkFile"} }
{ "keys": ["f4"], "command": "check_with_mk" , "args": {"function": "checkAll"} }
    """
    def run(self, edit, function):
        saver.saveAllDirty()
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

            sublime.message_dialog("Nun denn, ich konnte keine Fehler entdecken.\nHoffen wir, dass es auch wirklich keine gibt ;-).")
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
            if file_name and file_name.lower().endswith(".md"):
                path = os.path.dirname(self.view.window().active_view().file_name())
            else:
                sublime.error_message("Öffnen Sie eine Markdown-Datei um die Convertierung zu starten")
                return
        except OSError:
            sublime.error_message("Öffnen Sie eine Markdown-Datei um die Convertierung zu starten")
            return
        os.chdir(path)
        # just til gladtex is working well

        if(settings.get('use_gladtex')):
            p = pandoc.pandoc()
        else:
            p = pandoc.pandoc()
        try:
            p.convert_file(file_name)
        except FileNotFoundError as ex_message:
            sublime.error_message("Sie müssen Pandoc installieren.")
            return
        if(autoload_html):
            print("open in browser",file_name.replace(".md",".html"))
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
            print("open in browser",parent )
            Browser(parent)
        m = None


class InsertLinkPanelCommand(sublime_plugin.TextCommand):
    """
{ "keys": ["alt+shift+l"], "command": "insert_link_panel"}
    """
    def run(self, edit):
        self.counter = 0
        self.keys = ['url', 'linktext']
        #create Dictionary
        self.dictionary = {
            'url': Bunch(name='URL', value=''),
            'linktext': Bunch(name='Linktext', value=''),
        }
        if(settings.get("hints")):
                messageBox.showMessageBox("Sie wollen ein Link hinzufügen. Es sind 2 Eingaben erforderlich: \n"
                    "\t1. URL, http://www.tu-dresden.de  \n"
                  "\t2. Linktext, z.B. Webseite der TU Dresden \n")
        self.show_prompt()

    def show_prompt(self):
        self.view.window().show_input_panel(self.dictionary[self.keys[self.counter]].name, '', self.on_done, None, None)

    def check_user_input(self, key, content):
        return {
            'url': lambda s: s,
            'linktext': lambda s: s,
    }[key](content)

    def on_done(self,content):
        self.dictionary[self.keys[self.counter]].value = self.check_user_input(self.keys[self.counter], content)
        self.counter += 1
        if self.counter < (len(self.dictionary)):
            self.show_prompt()
        else:
            self.input_done()

    def input_done(self):
        url = self.dictionary['url'].value.lower()
        if(not url.startswith("http://") and not url.startswith("https://")):
            url = "http://"+url
        markdown = "[%s](%s)" % (self.dictionary['linktext'].value, url)
        self.view.run_command(
            "insert_my_text", {"args":
            {'text': markdown}})

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

class InsertImagePanelCommand(sublime_plugin.TextCommand):
    """
{ "keys": ["ctrl+alt+i"], "command": "insert__image_panel"}
    """
    def run(self, edit):
        # 0 is location of picture not a input_panel
        self.counter = 1
        self.keys = ['location', 'title', 'description']
        #create Dictionary
        self.dictionary ={
            'location': Bunch(name='Speicherort', value=''),
            'title': Bunch(name='Bildname', value=''),
            'description': Bunch(name='Bildbeschreibung', value=''),
        }
        self.imageFormats = settings.get("image_formats")
        self.imagefiles = self.getFileName(self.imageFormats)
        if self.imagefiles:
            if(settings.get("hints")):
                messageBox.showMessageBox("Sie wollen ein Bild hinzufügen. Es sind 3 Eingaben erforderlich: \n"
                "\t1. Speicherort des Bildes \n"
                "\t2. Name des Bildes \n"
                "\t3. Alternativbeschreibung zum Bild \n")
            self.show_prompt(self.imagefiles)
        else:
            dirname = os.path.dirname(self.view.file_name())
            dirname = os.path.join(dirname,"bilder")
            message = "Im Ordner Bilder sind keine Bilddaten gespeichert.\n"
            message += "Speichern zuerst Bilder in dem Ordner\n"
            message += dirname +"\n"
            message += "um ein Bild einfügen zu können."
            sublime.error_message(message)
            return

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

    def show_prompt(self, listFile):
        self.view.window().show_quick_panel(listFile,self.on_done_filename,sublime.MONOSPACE_FONT)

    def on_done_filename(self, input):
        if input == -1:  # esc
            #sublime.error_message("W?len Sie eine Bilddatei aus!")
            print("input = -1???")
        elif input != -1 :
            self.dictionary["location"].value = self.check_user_input(self.keys[0], self.imagefiles[input])
            self.show_prompt_image()

    def show_prompt_image(self):
        self.view.window().show_input_panel(self.dictionary[self.keys[self.counter]].name, '', self.on_done, None, None)

    def check_user_input(self, key, content):
        return {
        'location': lambda s: s,
        'title': lambda s: s,
        'description': lambda s: s,
        }[key](content)

    def on_done(self,content):
        self.dictionary[self.keys[self.counter]].value = self.check_user_input(self.keys[self.counter], content)
        self.counter += 1
        if self.counter < (len(self.dictionary)): # skip last index
            self.show_prompt_image()
        else:
            self.input_done()


    def input_done(self):
        """
        dictionary-content
        'location': Bunch(name='Speicherort', value=''),
                'title': Bunch(name='Bildname', value=''),
                'description': Bunch(name='Bildbeschreibung', value=''),
        }
        """
        message = ""
        img_desc = factories.ImageDescription(self.dictionary['location'].value)
        if img_desc.img_maxlength > len(self.dictionary['description'].value):
            img_desc.set_outsource_descriptions(False)
        else:
            img_desc.set_outsource_descriptions(True)
        img_desc.set_description(self.dictionary['description'].value)
        img_desc.set_title(self.dictionary['title'].value)
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
            fd.write("\n"+description)


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

class ImportCsvTableCommand(sublime_plugin.TextCommand):
    def run(self,edit):
        self.csvfiles = self.getCsvFile()
        if self.csvfiles and self.view.file_name().endswith("md"):
            if(settings.get("hints")):
                messageBox.showMessageBox("Sie wollen eine Tabelle aus einer CSV-Datei hinzufügen. \n"
                "Wählen Sie im folgenden Dialog die entsprechende Datei aus.")
            self.show_prompt(self.csvfiles)
        elif self.view.file_name().endswith("md"):
            dirname = os.path.dirname(self.view.file_name())
            dirname = os.path.join(dirname,settings.get("table_path"))
            message = "Im Ordner \"" + settings.get("table_path")+"\" sind keine csv-Dateien gespeichert.\n"
            message += "Speichern zuerst CSV-Dateien in dem Ordner\n"
            message += dirname +"!"
            sublime.error_message(message)
            return
        else:
            message = "Sie müssen eine Markdown-Datei(*.md) öffnen um,\n"
            message += "um eine Tabelle importieren zu können."
            sublime.error_message(message)
            return
    def show_prompt(self, listFile):
        self.view.window().show_quick_panel(listFile,self.on_done,sublime.MONOSPACE_FONT)

    def on_done(self,input):
        if input == -1:
            pass
        elif input != -1:
            self.CreateMarkdownFromCsv(os.path.join(self.table_path,self.csvfiles[input]))

    def getCsvFile(self):
        listFiles = []
        filename = self.view.file_name()
        self.table_path = ""
        if  filename is not None:
            path = os.path.dirname(self.view.window().active_view().file_name())
            self.table_path = os.path.join(path,settings.get("table_path"))
        for (dirname,dirs, files) in os.walk(self.table_path):
            for file in files:
                if file.lower().endswith("csv"):
                    listFiles.append(file)
        return listFiles

    def CreateMarkdownFromCsv(self,csvFilename):
        table_markdown = ""
        with open(csvFilename,newline="") as csvfile:
            reader = csv.reader(csvfile, delimiter = " ")
            for i,row in enumerate(reader):
                content = "".join(row)
                if i == 1:
                    # e.g. if there are 2 row_delimiter than there are 3 columns
                    # also 4 pipes '|'
                    columns = content.count(settings.get("row_delimiter"))+ 1
                    table_markdown += columns*'| -----------'+'|\n'
                table_markdown += "|" + "".join(row).replace(settings.get("row_delimiter"),"|")+ "|\n"
        self.view.run_command("insert_my_text", {"args":{'text': table_markdown}})

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

        #if(    settings.get("table_default_values"))
        markdown =""
        for r in range(0,rows):
            markdown += "|"
            for c in range(0,cols):
                cellValue = ""
                if( settings.get("table_default_values")):
                    cn = c + 1 #colnumber
                    rn = r + 1 #rownumber
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
{ "keys": ["alt+shift+f"], "command": "add_tag", "args": {"tag": "formula", "markdown_str":"$$"}}
{ "keys": ["alt+shift+u"], "command": "add_tag", "args": {"tag": "ul", "markdown_str":"- "} },
{ "keys": ["alt+shift+o"], "command": "add_tag", "args": {"tag": "ol", "markdown_str":"1. "} },
{ "keys": ["alt+shift+s"], "command": "add_tag", "args": {"tag": "strong+em", "markdown_str":"***"} },
    """
    def run(self, edit, tag, markdown_str):
        screenful = self.view.visible_region()
        (row,col) = self.view.rowcol(self.view.sel()[0].begin())
        target = self.view.text_point(row, 0)
        if not self.view.file_name().endswith("md"):
            return
        if tag in ['em', 'strong','formula','strong+em']:
            (row,col) = self.view.rowcol(self.view.sel()[0].begin())
            for region in self.view.sel():
                if not region.empty():
                    cursorPos = self.view.sel()
                    selString = self.view.substr(region)
                    word = self.view.word(target)
                    movecursor = len(word)
                    diff = 0
                    if movecursor > 0:
                        diff = movecursor/2
                        strg = str(diff)
                        target = self.view.text_point(row, diff)
                    if region.a < region.b:
                        firstPos =  region.a
                        endPos = region.b
                    else:
                        firstPos =  region.b
                        endPos = region.a
                    endPos += len(markdown_str)

                    self.view.sel().clear()
                    if not selString.startswith(markdown_str):
                        self.view.insert(edit,firstPos,markdown_str)
                        self.view.insert(edit,endPos,markdown_str)
                    self.view.sel().add(sublime.Region(cursorPos))

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





