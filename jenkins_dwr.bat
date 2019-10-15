call C:\ProgramData\Anaconda3\Scripts\activate.bat C:\ProgramData\Anaconda3
call conda create -n test_pyhecdss -y conda-build conda-verify numpy
call conda activate test_pyhecdss
call conda build conda.recipe
if errorlevel 1 exit 1
