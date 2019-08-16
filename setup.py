"""
setup.py file for SWIG example
"""

from distutils.core import setup, Extension
from distutils import sysconfig

# Third-party modules - we depend on numpy for everything
import re
import numpy

def get_numpy_include():
    # Obtain the numpy include directory.  This logic works across numpy versions.
    try:
        numpy_include = numpy.get_include()
    except AttributeError:
        numpy_include = numpy.get_numpy_include()
    return numpy_include


# check_numpy_i() #--This is failing due SSL certificate issue
#
pyheclib_module = Extension('pyhecdss._pyheclib',
                            sources=['pyhecdss/pyheclib.i',
                                     'pyhecdss/hecwrapper.c'],
                            swig_opts=['-python', '-py3'],
                            libraries=['extensions/heclib6-VE', 'ifconsol',
                                       'legacy_stdio_definitions', 'User32', 'gdi32', ],
                            library_dirs=[
                                r'd:\dev\pydss\swig', r'C:\Program Files (x86)\IntelSWTools\compilers_and_libraries\windows\compiler\lib\intel64'],
                            extra_link_args=['/FORCE:UNRESOLVED'],
                            include_dirs=[get_numpy_include()],
                            )

setup(name='pyhecdss',
      version='0.1',
      author="Nicky Sandhu",
      description="""Swig for HECLIB""",
      ext_modules=[pyheclib_module],
      packages=["pyhecdss"],
      )
