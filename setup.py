"""
setup.py file for SWIG example
"""

# from distutils.core import setup, Extension
import codecs
import os
import platform
import numpy
import versioneer
from setuptools import setup, Extension, find_packages


def get_numpy_include():
    try:
        return numpy.get_include()
    except AttributeError:
        numpy_include = numpy.get_numpy_include()
    return numpy_include


##------------------ VERSIONING BEST PRACTICES --------------------------##

here = os.path.abspath(os.path.dirname(__file__))


def read(*parts):
    with codecs.open(os.path.join(here, *parts), "r") as fp:
        return fp.read()


with open("README.rst") as readme_file:
    readme = readme_file.read()

with open("CHANGELOG.rst") as history_file:
    history = history_file.read()

requirements = ["numpy", "pandas"]

setup_requirements = []

test_requirements = ["pytest"]


##------------ COMPILE LINK OPTIONS for Linux and Windows ----------------#

if platform.system() == "Linux":
    # https://stackoverflow.com/questions/329059/what-is-gxx-personality-v0-for
    extra_links = ["-fno-exceptions", "-fno-rtti", "-shared", "-lgfortran", "-lstdc++"]
    libs = ["heclib6-WE"]  # linux
    libdirs = ["./extensions"]  # linux
    compile_args = ["-D_GNU_SOURCE", "-fno-exceptions"]  # linux
elif platform.system() == "Windows":
    extra_links = ["/NODEFAULTLIB:LIBCMT"]
    libs = [
        "extensions/heclib6-VE",
    ]
    libdirs = []
    compile_args = []
else:
    raise Exception("Unknown platform: " + platform.system() + "! You are on your own")


# check_numpy_i() #--This is failing due SSL certificate issue
#
pyheclib_module = Extension(
    "pyhecdss._pyheclib",
    sources=["pyhecdss/pyheclib.i", "pyhecdss/hecwrapper.c"],
    swig_opts=[
        "-py3",
    ],
    libraries=libs,
    library_dirs=libdirs,
    extra_compile_args=compile_args,
    extra_link_args=extra_links,
    include_dirs=[get_numpy_include()],
)

setup(
    version=versioneer.get_version(),
    cmdclass=versioneer.get_cmdclass(),
    ext_modules=[pyheclib_module],
)
