from distutils.core import setup
import py2exe
 
setup(
    console=[{"script":"z80GrinderConverter.py"}],
    options={"py2exe": {"includes":["sys","os"]}}
)