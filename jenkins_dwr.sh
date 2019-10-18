#!/bin/bash
source /etc/profile.d/modules.sh
module load python/miniconda3
conda create -n test_pyhecdss -y conda-build conda-verify numpy
source activate test_pyhecdss
conda build conda.recipe
