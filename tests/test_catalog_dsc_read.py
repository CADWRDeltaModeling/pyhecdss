import pyhecdss
import pandas as pd
import numpy as np
import os

def test_catalog_dsc_read():
    dh=pyhecdss.DSSFile('test_catalog.dss')
    dfc=dh._read_catalog_dsc('test_catalog.dsc')
    assert len(dfc) == 1
    assert dfc.loc[0,'D'] == '01NOV2002 - 01DEC2019'
