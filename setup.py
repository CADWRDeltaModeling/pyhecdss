import os
import platform
import numpy
import versioneer
from setuptools import setup, Extension, find_packages

def get_numpy_include():
    try:
        return numpy.get_include()
    except AttributeError:
        return numpy.get_numpy_include()

# Platform-specific compile and link options
if platform.system() == 'Linux':
    extra_links = ['-fno-exceptions', '-fno-rtti', '-shared', '-lgfortran', '-lstdc++']
    libs = ['heclib6-WE']
    libdirs = ['./extensions']
    compile_args = ['-D_GNU_SOURCE', '-fno-exceptions']
elif platform.system() == 'Windows':
    extra_links = ["/NODEFAULTLIB:LIBCMT"]
    libs = ['extensions/heclib6-VE']
    libdirs = []
    compile_args = []
else:
    raise Exception(f"Unknown platform: {platform.system()}! You are on your own")

pyheclib_module = Extension(
    'pyhecdss._pyheclib',
    sources=['pyhecdss/pyheclib.i', 'pyhecdss/hecwrapper.c'],
    swig_opts=[],
    libraries=libs,
    library_dirs=libdirs,
    extra_compile_args=compile_args,
    extra_link_args=extra_links,
    include_dirs=[get_numpy_include()],
)

setup(
    ext_modules=[pyheclib_module],
    cmdclass=versioneer.get_cmdclass(),
)
