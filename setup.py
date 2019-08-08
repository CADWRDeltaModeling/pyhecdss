"""
setup.py file for SWIG example
"""

from distutils.core import setup, Extension
from distutils      import sysconfig

# Third-party modules - we depend on numpy for everything
import re
import requests
import numpy

def check_numpy_i():
    np_version = re.compile(r'(?P<MAJOR>[0-9]+)\.'
                            '(?P<MINOR>[0-9]+)') \
                            .search(numpy.__version__)
    np_version_string = np_version.group()
    np_version_info = {key: int(value)
                       for key, value in np_version.groupdict().items()}

    np_file_name = 'numpy.i'
    np_file_url = 'https://raw.githubusercontent.com/numpy/numpy/maintenance/' + \
                  np_version_string + '.x/tools/swig/' + np_file_name
    if(np_version_info['MAJOR'] == 1 and np_version_info['MINOR'] < 9):
        np_file_url = np_file_url.replace('tools', 'doc')

    chunk_size = 8196
    with open(np_file_name, 'wb') as file:
        for chunk in requests.get(np_file_url,
                                  stream=True).iter_content(chunk_size):
            file.write(chunk)

def get_numpy_include():
    # Obtain the numpy include directory.  This logic works across numpy versions.
    try:
        numpy_include = numpy.get_include()
    except AttributeError:
        numpy_include = numpy.get_numpy_include()
    return numpy_include


#check_numpy_i() #--This is failing due SSL certificate issue
#
pyheclib_module = Extension('_pyheclib',
                           sources=['pyheclib.i','hecwrapper.c'],
                           libraries=['heclib6-VE','ifconsol','legacy_stdio_definitions','User32','gdi32',],
                           library_dirs=[r'd:\dev\pydss\swig',r'C:\Program Files (x86)\IntelSWTools\compilers_and_libraries\windows\compiler\lib\intel64'],
                           extra_link_args=['/FORCE:UNRESOLVED'],
                           include_dirs = [get_numpy_include()],
                           )

setup (name = 'pyheclib',
       version = '0.1',
       author      = "Nicky Sandhu",
       description = """Swig for HECLIB""",
       ext_modules = [pyheclib_module],
       py_modules = ["pyheclib"],
       )
