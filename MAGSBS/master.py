import MAGSBS
import os, sys, codecs

"""For documentation about this module, please refer the its classs master."""
_ = MAGSBS.config._

class NoLectureConfigurationError(Exception):
    pass

class Master():
    """m =Master(path)
m.run()

Take a directory and perform breath-first search to find the first
.lecture_meta_data.dcxml. In this depth, all directories are scanned for this
file so that we actually have multiple roots (a forest). This is necessary for
lectures containing e.g. lecture and exercise material.  For each root the
navigation bar and the table of contents is generated; afterwards all MarkDown
files are converted."""
    def __init__(self, path):
        self._roots = self.__findroot( path )
    def get_roots(self):
        return self._roots
    def __findroot(self, path):
        roots = []
        dirs = [path]
        go_deeper = True
        for dir in dirs:
            meta = [e for e in os.listdir(dir) if e ==
                    MAGSBS.config.CONF_FILE_NAME]
            if( meta ): # found, this is our root
                roots.append( dir )
                go_deeper = False
            else:
                if( go_deeper ):
                    dirs += [os.path.join(dir, e)  for e in os.listdir( dir ) \
                        if( os.path.isdir( os.path.join(dir, e)) )]
        found_md = False
        for dir, dlist, flist in os.walk( path ):
            for f in flist:
                if( f.endswith(".md") ):
                    found_md = True
                    break
        if( roots == [] and found_md ):
            # this is markdown stuff without configuration!
            raise NoLectureConfigurationError("No configuration in a directory of the path \"%s\" or its subdirectories found. As soon as there are MarkDown files present, a configuration has to exist." % path)
        return roots

    def run(self):
        """This function should be used with great care. It shall only be run from
the root of a lecture. All other attempts will destroy the navigation links and
result in other undefined behavior.

This function creates a navigation bar, the table of contents and converts all
files. It will raise NoLectureConfigurationError when no configuration has been
found and there are MarkDown files."""
        c = convert_a_directoryl( self.get_roots() )
        cwd = os.getcwd()
        for root in c.get_roots():
            os.chdir( root )
            # create navigation bar
            p = MAGSBS.filesystem.page_navigation( "." )
            p.iterate()
            # create table of contents
            c = MAGSBS.filesystem.create_index( "." )
            c.walk()
            idx = MAGSBS.factories.index2markdown_TOC(c.get_index())
            with codecs.open( _( "index" ).lower() + ".md", 'w' ) as file:
                file.write( idx.get_markdown_page() )
            
            for dir, dlist, flist in MAGSBS.filesystem.get_markdown_files( ".", True ):
                os.chdir( dir )
                for f in flist:
                    p = MAGSBS.pandoc.pandoc()
                    p.convert( f )
                os.chdir( root )
        os.chdir( cwd )
        
