rem only needed if you add submodules etc..
sphinx-apidoc -o . ../pyhecdss
call make clean
call make html
call xcopy /y /s /e _build\* ..\docs
