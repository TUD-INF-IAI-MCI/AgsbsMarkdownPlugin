from distutils.core import setup
import sys, os

#path = os.path.dirname( sys.argv[0] )
#path = os.path.split( path )[0]
#path ) # add src root to also install MAGSBS

if(sys.platform.lower().find('win')>= 0):
    scripts = [os.path.join('cli','matuc.py')],
    packages = ['MAGSBS']
    modules = []
else:
    # on UNIX, we want a nice shell script ;)
    sys.path.append( 'cli' )
    scripts = [os.path.join('bin','matuc')]
    packages = ['MAGSBS']
    modules = ['matuc']

# install MAGSBS-module

setup(name='MAGSBS',
      version='0.1',
      packages=packages,
      )

# matuc distribution:
os.chdir('cli')
setup(name='MAGSBS/matuc',
      version='0.1',
      py_modules = modules,
      scripts=scripts
      )

