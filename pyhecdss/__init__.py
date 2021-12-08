__author__ = """Nicky Sandhu"""
__email__ = 'psandhu@water.ca.gov'

from ._version import get_versions
__version__ = get_versions()['version']
del get_versions

from .pyhecdss import DATE_FMT_STR, DSSData, DSSFile, get_matching_ts, get_start_end_dates, get_ts, get_version, monthrange, set_message_level, set_program_name

set_message_level(0)
