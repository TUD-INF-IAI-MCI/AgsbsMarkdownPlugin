import sys
import sublime

VERSION = int(sublime.version())

mod_prefix = "agsbs_infrastructure.MAGSBS"
reload_mods = []

if VERSION > 3000:
    mod_prefix = "AgsbsMarkdownPlugin." + mod_prefix
    from imp import reload
    for mod in sys.modules:
        if mod[0:24] == 'AgsbsMarkdownPlugin' and sys.modules[mod] is not None:
            reload_mods.append(mod)
else:

    for mod in sorted(sys.modules):
        if mod[0:26] == 'AgsbsMarkdownPlugin' and sys.modules[mod] is not None:
            reload_mods.append(mod)

mods_load_order = [
    '.config',
    '.pandoc',
    '.errors',
    '.quality_assurance',
    '.matuc',
    '.mparser',
    '.pandocfilters',
    '.contentfilter',
    '.master',
    '.config',
    '.meta',
    '.datastructure',
    '.filesystem'
]

for suffix in mods_load_order:    
    mod = mod_prefix + suffix   
    if mod in reload_mods:
        print(mod)
        reload(sys.modules[mod])