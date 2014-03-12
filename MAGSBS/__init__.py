# -*- coding: utf-8 -*-

"""Getting started:

# create index:
c = create_index('.')
c.walk()

# index 2 markdown:
md = index2markdown_TOC(c.get_data(), 'de')
my_fancy_page = c.get_markdown_page()
"""

import os, sys, codecs, re
import collections

# internal imports
from filesystem import *
from factories import *
import factories
import pandoc
import config


#__all__ = ['config, 'pandoc']

