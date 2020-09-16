__author__ = """Nicky Sandhu"""
__email__ = 'psandhu@water.ca.gov'

from ._version import get_versions
__version__ = get_versions()['version']
del get_versions

from .pyhecdss import *
set_message_level(0)

