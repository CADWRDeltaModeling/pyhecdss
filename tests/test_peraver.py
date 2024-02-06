import pyhecdss
import pandas as pd
import numpy as np
import os


def test_read_write_cycle_rts():
    '''
    Test reading and writing of period time stamped data so
    that reads and writes don't result in shifting the data
    '''
    fname = "test2.dss"
    if os.path.exists(fname):
        os.remove(fname)
    path = '/SAMPLE/SIN/WAVE/01JAN1990 - 01JAN1990/15MIN/SAMPLE1/'
    sina = np.sin(np.linspace(-np.pi, np.pi, 201))
    dfr = pd.DataFrame(sina,
                       index=pd.period_range('01jan1990 0100', periods=len(sina), freq='15min'),
                       columns=[path])

    d = pyhecdss.DSSFile(fname, create_new=True)
    unit2, ptype2 = 'UNIT-X', 'PER-VAL'
    d.write_rts(path, dfr, unit2, ptype2)
    d.close()
    #
    d2 = pyhecdss.DSSFile(fname)
    plist2 = d2.get_pathnames()
    path = plist2[0]
    dfr2, unit2, ptype2 = d.read_rts(path)
    pd.testing.assert_frame_equal(dfr, dfr2)
