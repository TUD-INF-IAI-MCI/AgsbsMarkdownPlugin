import sublime, sublime_plugin
import importlib
import sys,os,imp

PACKAGE_PARENT = ""
SCRIPT_DIR = os.path.dirname(os.path.realpath(os.path.join(os.getcwd(), os.path.expanduser(__file__))))
print(SCRIPT_DIR)
sys.path.append(os.path.normpath(os.path.join(SCRIPT_DIR, PACKAGE_PARENT)))
#from MAGSBS.test import nix #
#from MAGSBS.test import print_mode_t
#from MAGSBS.test import juhu 
#from MAGSBS.test import * 


# execute pluing view.run_command("example")
class ExampleCommand(sublime_plugin.TextCommand):
	def run(self, edit):
		
		#foo = importlib.import_module("MAGSBS")
		#self.GetModules()
		self.openCMD()
		self.SaveDirties()
		#self.createOutPut()
		self.showOverlay()
	def GetModules(self):
		
		#from MAGSBS.test import juhu # lädt module, aber refreshet nicht

		#imp.reload(MAGSBS.test)
		#print_mode("//asd")
		print_mode_t("//asd")
		nix("HOPE")
		print(juhu("max"))

	def openCMD(self):
		self.view.window().run_command("show_panel",{"panel": "console"});
		print("\n#################################\n")
		print("ERROR")
		print("\n#################################\n")

	def SaveDirties(self):
		"""
			Save all dirty views
		"""
		#self.view.run_command("save_all")

		for w in sublime.windows():
			for v in w.views():
				if v.file_name():
					if v.is_dirty():						
						v.run_command("save")
				else:
					print("es gibt geöffnet buffer ohne namen")

	def createOutPut(self):
		self.view.window().create_output_panel("name")
		#self.view.window().run_command("show_panel",{"panel": "output.name"});
		self.view.window().show_input_panel("Bild-URL", "Name der Bilddatei eintragen. z.b. bild.jpg", None, None, None)  

	def showOverlay(self):
		self.view.window().run_command("show_overlay",{"overlay": "goto", "show_files": "true" });
		
			#{ "keys": ["ctrl+shift+p"], "command": "show_overlay", "args": {"overlay": "command_palette"} },

