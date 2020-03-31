rem setup development environment
conda create -n dev_pyhecdss
conda activate dev_pyhecdss
conda install -c defaults -c conda-forge conda conda-build nbsphinx numpy pandas sphinx
rem conda install pytest-runner
rem conda install -c defaults -c conda-forge swig>=4