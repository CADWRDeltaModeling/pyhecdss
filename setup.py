"""
setup.py file for SWIG example
"""

#from distutils.core import setup, Extension
import codecs
import os
import platform
import versioneer
from setuptools import setup, Extension, find_packages

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


##------------------ VERSIONING BEST PRACTICES --------------------------##

here = os.path.abspath(os.path.dirname(__file__))


def read(*parts):
    with codecs.open(os.path.join(here, *parts), 'r') as fp:
        return fp.read()


with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('CHANGELOG.rst') as history_file:
    history = history_file.read()

requirements = ["numpy>=1.16,<2", "pandas>=0.23"]

setup_requirements = ['pytest-runner>=5.0', ]

test_requirements = ['pytest', ]


##------------ COMPILE LINK OPTIONS for Linux and Windows ----------------#

if platform.system() == 'Linux':
    # https://stackoverflow.com/questions/329059/what-is-gxx-personality-v0-for
    extra_links = ['-fno-exceptions', '-fno-rtti', '-shared',
                   '-lgfortran', '-lstdc++']
    libs = ['heclib6-WE']  # linux
    libdirs = ['./extensions']  # linux
    compile_args = ['-D_GNU_SOURCE', '-fno-exceptions']  # linux
elif platform.system() == 'Windows':
    extra_links = ['/FORCE:UNRESOLVED']  # windows
    libs = ['extensions/heclib6-VE', 'extensions/ifconsol', 'extensions/libifcoremt', 'extensions/libifport', 'extensions/libmmt',
            'extensions/libirc', 'extensions/svml_disp', 'extensions/IFWIN', 'legacy_stdio_definitions', 'User32', 'gdi32', ]  # windows
    libdirs = [r'd:\dev\pydss\swig',
               r'C:\Program Files (x86)\IntelSWTools\compilers_and_libraries\windows\compiler\lib\intel64']  # windows
    compile_args = []  # windows
else:
    raise Exception("Unknown platform: "+platform.system()+"! You are on your own")


# check_numpy_i() #--This is failing due SSL certificate issue
#
pyheclib_module = Extension('pyhecdss._pyheclib',
                            sources=['pyhecdss/pyheclib.i',
                                     'pyhecdss/hecwrapper.c'],
                            swig_opts=['-py3', ],
                            libraries=libs,
                            library_dirs=libdirs,
                            extra_compile_args=compile_args,
                            extra_link_args=extra_links,
                            include_dirs=[get_numpy_include()],
                            )

setup(name='pyhecdss',
      author="Nicky Sandhu",
      author_email='psandhu@water.ca.gov',
      version=versioneer.get_version(),
      cmdclass=versioneer.get_cmdclass(),
      classifiers=[
          'Development Status :: 2 - Pre-Alpha',
          'Intended Audience :: Developers',
          'License :: OSI Approved :: MIT License',
          'Natural Language :: English',
          'Programming Language :: Python :: 3',
          'Programming Language :: Python :: 3.4',
          'Programming Language :: Python :: 3.5',
          'Programming Language :: Python :: 3.6',
          'Programming Language :: Python :: 3.7',
      ],
      description="For reading/writing HEC-DSS files",
      install_requires=requirements,
      license="MIT license",
      long_description=readme + '\n\n' + history,
      include_package_data=True,
      keywords='pyhecdss',
      packages=find_packages(include=['pyhecdss']),
      setup_requires=setup_requirements,
      python_requires='~=3.5',
      test_suite='tests',
      tests_require=test_requirements,
      url='https://github.com/dwr-psandhu/pyhecdss',
      zip_safe=False,
      ext_modules=[pyheclib_module],
      )
