REM set PATH=d:\Programs\swigwin-4.0.0;%PATH%
python setup.py build_ext --inplace
python setup.py install --single-version-externally-managed --record=record.txt
if errorlevel 1 exit 1
