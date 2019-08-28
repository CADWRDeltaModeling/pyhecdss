========
pyhecdss
========


.. image:: https://img.shields.io/pypi/v/pyhecdss.svg
        :target: https://pypi.python.org/pypi/pyhecdss

.. image:: https://readthedocs.org/projects/pyhecdss/badge/?version=latest
        :target: https://pyhecdss.readthedocs.io/en/latest/?badge=latest
        :alt: Documentation Status


For reading/writing HEC-DSS files [https://www.hec.usace.army.mil/software/hec-dss/]
HEC-DSS is an ancient database used by the Army Corps of Engineers and prevalent
in water related models. This module is a bridge to read and write time series
data from this data format and read it into pandas DataFrame

* Free software: MIT license
* Documentation: https://pyhecdss.readthedocs.io.


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
.. _Swig: http://www.swig.org/
