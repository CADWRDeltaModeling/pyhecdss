import pyhecdss
import pandas as pd
import numpy as np
import os


def test_catalog_dsc_read():
    dfc = pyhecdss.DSSFile._read_catalog_dsc('test_catalog.dsc')
    assert len(dfc) == 1
    assert dfc.loc[0, 'D'] == '01NOV2002 - 01DEC2019'


def test_catalog_dsc_read_failing():
    '''
    Case with missing T column. Looks like its an option when cataloging a DSS file
    '''
    dfc = pyhecdss.DSSFile._read_catalog_dsc('test_failing_catalog.dsc')
    assert len(dfc) == 4
    assert dfc.loc[0, 'D'] == '01JAN1915 - 01JAN2015'
