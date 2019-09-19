.. highlight:: shell

============
Installation
============


Stable release
--------------

To install pyhecdss, run this command in your terminal:

.. code-block:: console

    $ conda install -c cadwr-dms pyhecdss
    $ conda install -c anaconda libgfortran # May be needed on linux if libgfortran is not installed along with gcc

This is the preferred method to install pyhecdss, as it will always install the most recent stable release.

If you don't have `conda`_ installed, this `Python installation guide`_ can guide
you through the process.

.. _conda: https://docs.conda.io/projects/conda/en/latest/user-guide/install/
.. _Python installation guide: http://docs.python-guide.org/en/latest/starting/installation/


From sources
------------

The sources for pyhecdss can be downloaded from the `Github repo`_.

You can either clone the public repository:

.. code-block:: console

    $ git clone https://github.com/CADWRDeltaModeling/pyhecdss.git

Or download the `tarball`_:

.. code-block:: console

    $ curl  -OL https://github.com/CADWRDeltaModeling/pyhecdss/tarball/master

Once you have a copy of the source, you can install it with:

.. code-block:: console

    $ python setup.py install

This library has dependencies on Intel Fortran AND Intel Compiler for Windows and Intel Parallel Composer libraries. You will need the following
libraries 

.. code-block::

     setup.py changes --
     libs = ['extensions/heclib6-VE', 'extensions/ifconsol','extensions/libifcoremt',
             'extensions/libifport','extensions/libmmt','extensions/libirc',
             'extensions/svml_disp','extensions/IFWIN','legacy_stdio_definitions',
             'User32', 'gdi32', ] 

.. _Github repo: https://github.com/CADWRDeltaModeling/pyhecdss
.. _tarball: https://github.com/CADWRDeltaModeling/pyhecdss/tarball/master
