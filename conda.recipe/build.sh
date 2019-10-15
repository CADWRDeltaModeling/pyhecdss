#!/bin/bash
python setup.py build_ext --inplace
python setup.py install --single-version-externally-managed --record=record.txt # [unix]
