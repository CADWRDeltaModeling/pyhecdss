=========
CHANGELOG
=========
0.6.1
-----
 fixed bug when switching to non-condensed catalog that caused shortening of time windows
 
0.6.0
-----
 * fix for breaking change by pandas >= 1.1
 * switching to using non-condensed catalog, flag available to switch back
 * changing exception on missing pathname to logging message
 * changing message level to 0 as default
 * adding get_rts_matching for pathname selection by regular expressions
 * replaced warnings with debug logging

0.5.1
-----
Fixed for '*' in catalog file in case of missing periods

0.5.0
-----
Added helper function for simple timeseries retrieval

0.4.1
-----
regular and irregular timeseries now share same time window parsing logic

0.4.0
-----
fixes for issue #16: pandas timestamp limitations

0.3.1
-----
another fix for pandas 1.0.0 upgrade - issue #15

0.3.0
-----
fix for issue 15: units 'M' and 'Y' no longer supported

0.2.9
-----
Fixed issue with end of timestamp writing to dss files for "PER-*" data type

0.2.8
-----
Recompiled heclib in linux with latest compilers to resolve issue 8

0.2.7
-----
Partial fixes for offset: Fixed for INST-* timeseries but not PER-* timeseries (issue #12)

0.2.6
-----
Performance tests added to showcase pyhecdss is the fastest
Fixed issue #10: Period data stored shifted to end of time stamp (HEC-DSS convention)
Fixing libgfortran dependency on linux by statically linking the library

0.2.5
-----
Merged pull request from HenryDane:
issues warnings or throws exception based on return value from functions
fixed minor typo(s), added tests

0.2.4
-----

Fixes issues #2, #4: get_version(), set_message_level(), set_program_name() now supported at module level
Fixes issues #1: HECDSS marks periods by end of time stamp bug

0.2.3
-----
Added linux 64bit support
Corrected license to MIT for conda distribution

0.2.2
-----
Update tests to use a smaller test.dss files
Added sphinx documentation and demo notebook

0.2.1
-----
Write irregular time series

0.2.0
------
Write regular time series
Read irregular time series as data frame + units + type
Performance improvement to using np.zeros instead of np.array(range...)

0.1.6
-----
