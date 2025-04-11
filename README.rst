========
pyhecdss
========

>  **Note:** This project only supports **DSS version 6** and now recommends users to `HEC-DSS Python`_ version 7 and higher

For reading/writing HEC-DSS files [https://www.hec.usace.army.mil/software/hec-dss/]
HEC-DSS is an ancient database used by the Army Corps of Engineers and prevalent
in water related models. This module is a bridge to read and write time series
data from this data format and read it into pandas DataFrame

* Free software: MIT license
* Documentation: https://cadwrdeltamodeling.github.io/pyhecdss/


Installation
------------
> **Warning:** pip installs do not work. Please use conda installs from the cadwr-dms channel

``conda create -c conda-forge -c cadwr-dms -n test_pyhecdss python=3.12 pyhecdss``

Features
--------

* Open and close DSS files
* Read catalog of DSS files as pandas DataFrame
* Read and write time series from DSS files

Limitations
-----------

* Only support for Python 3 - 64 bit for windows and linux
* Relies on pre-compiled libraries the source distribution of which is not allowed

Credits
-------

This package wraps the `HEC-DSS Software`_ using the `Swig`_ library.

This package was created with Cookiecutter_ and the `audreyr/cookiecutter-pypackage`_ project template.

.. _Cookiecutter: https://github.com/audreyr/cookiecutter
.. _`audreyr/cookiecutter-pypackage`: https://github.com/audreyr/cookiecutter-pypackage
.. _`HEC-DSS Software`: https://www.hec.usace.army.mil/software/hec-dss/
.. _`HEC-DSS Python`: https://github.com/HydrologicEngineeringCenter/hec-dss-python
.. _Swig: http://www.swig.org/
