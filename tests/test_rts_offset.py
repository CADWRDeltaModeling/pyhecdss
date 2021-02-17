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


def cleanup(file):
    try:
        os.remove(file)
    except:
        pass


def test_store_as_instval(tsdaily):
    dssfilename = 'test_offset.dss'
    cleanup(dssfilename)
    with pyhecdss.DSSFile(dssfilename, create_new=True) as dssfh:
        pathname = tsdaily.columns[0]
        dssfh.write_rts(pathname, tsdaily, 'XXX', 'INST-VAL')
    with pyhecdss.DSSFile(dssfilename) as dssfh:
        dfcat = dssfh.read_catalog()
        plist = dssfh.get_pathnames(dfcat[dfcat.F == 'TEST-OFFSET'])
        assert len(plist) == 1
        df, cunits, ctype = dssfh.read_rts(plist[0])
    assert cunits == 'XXX'
    assert ctype == 'INST-VAL'
    pd.testing.assert_series_equal(tsdaily.iloc[:, 0], df.iloc[:, 0], check_names=False)


def test_store_as_perval(tsdaily):
    dssfilename = 'test_offset.dss'
    cleanup(dssfilename)

    with pyhecdss.DSSFile(dssfilename, create_new=True) as dssfh:
        pathname = tsdaily.columns[0]
        dssfh.write_rts(pathname, tsdaily, 'XXX', 'PER-VAL')
    with pyhecdss.DSSFile(dssfilename) as dssfh:
        dfcat = dssfh.read_catalog()
        plist = dssfh.get_pathnames(dfcat[dfcat.F == 'TEST-OFFSET'])
        assert len(plist) == 1
        df, cunits, ctype = dssfh.read_rts(plist[0])
    assert cunits == 'XXX'
    assert ctype == 'PER-VAL'
    # --FIXME -- this is asserting as fail: see issue https://github.com/CADWRDeltaModeling/pyhecdss/issues/12
    with pytest.raises(AssertionError):
        pd.testing.assert_frame_equal(tsdaily, df, check_names=False, check_column_type=False)


def test_store_and_read():
    dssfilename = 'testbug1.dss'
    cleanup(dssfilename)
    arr = np.array([1.0, 2.0, 3.0])
    dfr = pd.DataFrame(arr, index=pd.period_range('NOV1990', periods=len(arr), freq='1M'))
    with pyhecdss.DSSFile(dssfilename, create_new=True) as d:
        d.write_rts('/SAMPLE0/ARR/OP//1MON//', dfr, '', 'PER-AVER')
    with pyhecdss.DSSFile(dssfilename) as d:
        catdf = d.read_catalog()
        plist = d.get_pathnames(catdf)
        dfr2, units, type = d.read_rts(plist[0])
    pd.testing.assert_series_equal(dfr.iloc[:, 0], dfr2.iloc[:, 0], check_names=False)
