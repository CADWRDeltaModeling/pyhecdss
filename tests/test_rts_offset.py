'''
Test regular time series with offset

This a time series that is say daily but the timestamp for the period
is say an hour before the end of the day

'''
import pytest
import pyhecdss
import numpy as np
import pandas as pd
import os


@pytest.fixture
def tsdaily():
    return pd.DataFrame(np.array([1, 2, 3, 4, 5], 'd'),
                        index=pd.date_range('01jan1970 2300', periods=5, freq='D'),
                        columns=['/A/B-INSTVAL/C/01JAN1970/1DAY/TEST-OFFSET/'])


def test_store_as_instval(tsdaily):
    dssfh = pyhecdss.DSSFile('test_offset.dss')
    pathname = tsdaily.columns[0]
    dssfh.write_rts(pathname, tsdaily, 'XXX', 'INST-VAL')
    dssfh.close()
    dssfh = pyhecdss.DSSFile('test_offset.dss')
    dfcat = dssfh.read_catalog()
    plist = dssfh.get_pathnames(dfcat[dfcat.F == 'TEST-OFFSET'])
    assert len(plist) == 1
    df, cunits, ctype = dssfh.read_rts(plist[0])
    assert cunits == 'XXX'
    assert ctype == 'INST-VAL'
    pd.testing.assert_frame_equal(tsdaily, df, check_names=False, check_column_type=False)


def test_store_as_instval(tsdaily):
    dssfh = pyhecdss.DSSFile('test_offset.dss', create_new=True)
    pathname = tsdaily.columns[0]
    dssfh.write_rts(pathname, tsdaily, 'XXX', 'PER-VAL')
    dssfh.close()
    dssfh = pyhecdss.DSSFile('test_offset.dss')
    dfcat = dssfh.read_catalog()
    plist = dssfh.get_pathnames(dfcat[dfcat.F == 'TEST-OFFSET'])
    assert len(plist) == 1
    df, cunits, ctype = dssfh.read_rts(plist[0])
    assert cunits == 'XXX'
    assert ctype == 'PER-VAL'
    # --FIXME -- this is asserting as fail: see issue https://github.com/CADWRDeltaModeling/pyhecdss/issues/12
    with pytest.raises(AssertionError):
        pd.testing.assert_frame_equal(tsdaily, df, check_names=False, check_column_type=False)
