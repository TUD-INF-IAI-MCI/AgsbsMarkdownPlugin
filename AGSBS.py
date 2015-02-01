# -*- coding: utf-8 -*-
import sublime, sublime_plugin
import os
import re
import codecs, re, sys
#import collections
#import json
import subprocess
import glob

from .agsbs_infrastructure.MAGSBS import master
from .agsbs_infrastructure.MAGSBS import config as config
from .agsbs_infrastructure.MAGSBS import pandoc
from .agsbs_infrastructure.MAGSBS import filesystem
"""
{ "keys": ["F2"], "command": "run_magsbs"}
"""
class CreateStructureCommand(sublime_plugin.TextCommand):
    def run(self,edit):
        path = os.path.dirname(self.view.window().active_view().file_name())
        path = os.path.join(path,"examples")
        os.chdir(path)
        inst = config.confFactory()
        inst = inst.get_conf_instance()
        inst.write()
"""
    { "keys": ["f3"], "command": "create_lecture"},
"""
class CreateLectureCommand(sublime_plugin.TextCommand):
    def run(self,edit):
        builder = filesystem.init_lecture("test",5,lang='en')
        builder.set_has_preface(False)
        builder.generate_structure()

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
        #config.LectureMetaData(config.CONF_FILE_NAME)
        #m = master.Master(path)

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