from pyhecdss.pyhecdss import DSSFile
import unittest
import pytest
import pyhecdss
import numpy as np
import pandas as pd
import os


class TestPyDsUtilsBasic(unittest.TestCase):

    def cleanTempFiles():
        file_list = ['./test_rts1.dss',
                     './test_rts1.dsc',
                     './test_rts1.dsd',
                     './test_its1.dss',
                     './test_its1.dsc',
                     './test_its1.dsd',
                     './test.dsc',
                     './test.dsd',
                     './test.dsc',
                     './test.dsd',
                     './test.dsk',
                     './test_offset.dss',
                     './test_rts1.dss',
                     './test2.dss',
                     './testnew.dss']

        for file in file_list:
            try:
                os.remove(file)
            except OSError:
                pass

    @ classmethod
    def setupClass(cls):
        cls.cleanTempFiles()

    @ classmethod
    def tearDownClass(cls):
        cls.cleanTempFiles()

    def test_with(self):
        with pyhecdss.DSSFile('test1.dss') as d:
            assert len(d.read_catalog()) > 0

    def test_open_close(self):
        fname = "test1.dss"
        dssfile = pyhecdss.DSSFile(fname)
        dssfile.open()
        dssfile.close()

    def test_catalog(self):
        fname = "test1.dss"
        with pyhecdss.DSSFile(fname) as dssfile:
            dssfile.catalog()
        self.assertTrue(os.path.exists('test1.dsc'))
        self.assertTrue(os.path.exists('test1.dsd'))

    def test_read_ts(self):
        fname = "test1.dss"
        pathname = '/SAMPLE/SIN/WAVE/01JAN1990/15MIN/SAMPLE1/'
        sdate = '01JAN1990'
        edate = '31JAN1990'
        with pyhecdss.DSSFile(fname) as dssfile:
            values, units, periodtype = dssfile.read_rts(pathname, sdate, edate)
        self.assertEqual(units, 'UNIT-X')
        self.assertEqual(periodtype, 'INST-VAL')
        self.assertEqual(len(values['10JAN1990': '11JAN1990'].values),
                         96*2)  # 96 15 min values per day
        # get series
        vseries = values.iloc[:, 0]
        self.assertTrue(abs(vseries.at['01JAN1990 0430']-(-0.42578)) < 1e-03)

    def test_write_ts(self):
        fname = "test_rts1.dss"
        pathname = '/TEST1/ONLY1/VANILLA//1DAY/JUST-ONES/'
        startDateStr, endDateStr = '01JAN1990 0100', '01JAN1991 0100'
        dtr = pd.date_range(startDateStr, endDateStr, freq='1D')
        df = pd.DataFrame(np.ones(len(dtr), 'd'), index=dtr)
        cunits, ctype = 'CCC', 'INST-VAL'
        with pyhecdss.DSSFile(fname, create_new=True) as dssfile2:
            dssfile2.write_rts(pathname, df, cunits, ctype)
        startDateStr = "01JAN1990"
        endDateStr = "01JAN1991"
        with pyhecdss.DSSFile(fname) as dssfile1:
            df2, cunits2, ctype2 = dssfile1.read_rts(pathname, startDateStr, endDateStr)
        self.assertEqual(ctype, ctype2)
        self.assertEqual(cunits, cunits2)
        self.assertEqual(1, df.iloc[0, 0])

    def test_write_rts_series(self):
        '''
        write_rts should work with pandas.Series as well.
        '''
        fname = "test_rts1.dss"
        pathname = '/TEST1/ONLY1/VANILLA//1DAY/JUST-ONES-SERIES/'
        startDateStr, endDateStr = '01JAN1990 0100', '01JAN1991 0100'
        dtr = pd.date_range(startDateStr, endDateStr, freq='1D')
        s = pd.Series(np.ones(len(dtr), 'd'), index=dtr)
        cunits, ctype = 'CCC', 'INST-VAL'
        with pyhecdss.DSSFile(fname, create_new=True) as dssfile2:
            dssfile2.write_rts(pathname, s, cunits, ctype)
        startDateStr = "01JAN1990"
        endDateStr = "01JAN1991"
        with pyhecdss.DSSFile(fname) as dssfile1:
            df2, cunits2, ctype2 = dssfile1.read_rts(pathname, startDateStr, endDateStr)
        self.assertEqual(ctype, ctype2)
        self.assertEqual(cunits, cunits2)
        self.assertEqual(1, s.iloc[0])

    def test_read_its(self):
        fname = "test1.dss"
        pathname = '/SAMPLE/ITS1/RANDOM/01JAN1990 - 01JAN1992/IR-YEAR/SAMPLE2/'
        with pyhecdss.DSSFile(fname) as dssfile:
            values, units, periodtype = dssfile.read_its(pathname)
        self.assertEqual(units, 'YYY')
        self.assertEqual(periodtype, 'INST-VAL')
        self.assertEqual(len(values), 3)
        # get series
        vseries = values.iloc[:, 0]
        self.assertTrue(abs(vseries.at['01JAN1990 0317']-1.5) < 1e-03)
        self.assertTrue(abs(vseries.at['05SEP1992 2349']-2.7) < 1e-03)

    def test_read_its_tw(self):
        # issue #26
        fname = "test1.dss"
        pathname = '/SAMPLE/ITS1/RANDOM/01JAN1990 0143 - 01JAN1992/IR-YEAR/SAMPLE2/'
        with pyhecdss.DSSFile(fname) as dssfile:
            values, units, periodtype = dssfile.read_its(pathname)
        self.assertEqual(units, 'YYY')
        self.assertEqual(periodtype, 'INST-VAL')
        self.assertEqual(len(values), 3)

    def test_write_its(self):
        fname = "test1.dss"
        pathname = '/TEST/ITS1/VANILLA//IR-YEAR/RANDOM/'
        ta = pd.to_datetime(['01apr1990', '05nov1991', '07apr1997'], format='%d%b%Y')
        df = pd.DataFrame([0.5, 0.6, 0.7], index=ta, columns=["random"])
        cunits, ctype = 'CCC', 'INST-VAL'
        with pyhecdss.DSSFile(fname) as dssfile2:
            dssfile2.write_its(pathname, df, cunits, ctype)
        with pyhecdss.DSSFile(fname) as dssfile1:
            df2, cunits2, ctype2 = dssfile1.read_its(pathname, "01JAN1990", "01JAN1998")
        self.assertEqual(ctype, ctype2)
        self.assertEqual(cunits, cunits2)
        self.assertEqual(df2.iloc[0, 0], df.iloc[0, 0])
        self.assertEqual(df2.iloc[1, 0], df.iloc[1, 0])
        self.assertEqual(df2.iloc[2, 0], df.iloc[2, 0])

    def test_write_its_series(self):
        fname = "test1.dss"
        pathname = '/TEST/ITS1/VANILLA//IR-YEAR/RANDOM/'
        ta = pd.to_datetime(['01apr1990', '05nov1991', '07apr1997'], format='%d%b%Y')
        df = pd.Series([0.5, 0.6, 0.7], index=ta)
        cunits, ctype = 'CCC', 'INST-VAL'
        with pyhecdss.DSSFile(fname) as dssfile2:
            dssfile2.write_its(pathname, df, cunits, ctype)
        with pyhecdss.DSSFile(fname) as dssfile1:
            df2, cunits2, ctype2 = dssfile1.read_its(pathname, "01JAN1990", "01JAN1998")
        self.assertEqual(ctype, ctype2)
        self.assertEqual(cunits, cunits2)
        self.assertEqual(df2.iloc[0, 0], df.iloc[0])
        self.assertEqual(df2.iloc[1, 0], df.iloc[1])
        self.assertEqual(df2.iloc[2, 0], df.iloc[2])

    def test_read_catalog(self):
        fname = "test1.dss"
        with pyhecdss.DSSFile(fname) as dssfile:
            df = dssfile.read_catalog()
        self.assertTrue(len(df) >= 1)

    def test_get_pathnames(self):
        fname = "test1.dss"
        with pyhecdss.DSSFile(fname) as dssfile:
            pathnames = dssfile.get_pathnames()
        self.assertTrue(len(pathnames) > 0)

    def test_version(self):
        fname = "test1.dss"
        cver, iver = pyhecdss.get_version(fname)
        self.assertEqual(6, iver)
        self.assertEqual('6-VE', cver)

    def test_set_message_level(self):
        fname = "test1.dss"
        print("No easy way to check automatically. Just look at screen and see if lot of messages are printed?")
        pyhecdss.set_message_level(10)
        with pyhecdss.DSSFile(fname) as d1:
            d1.close()
        print('No easy way to check automatically. Just look at screen and no DSS messages should be printed')
        pyhecdss.set_message_level(0)
        with pyhecdss.DSSFile(fname) as d1:
            d1.close()

    def test_except_on_bad_path(self):
        fname = "test1.dss"
        dssfile = pyhecdss.DSSFile(fname)
        pathname = '/SAMPLE/INVALID_MARKER/WAVE/01JAN1990/15MIN/SAMPLE1/'
        sdate = '01JAN1990'
        edate = '31JAN1990'
        # changed to a debugging level message so no error is now raised on missing pathname
        # values,units,periodtype=dssfile.read_rts(pathname,sdate,edate)

    def test_missing_dir(self):
        '''
        missing directory in filename causes crash. So check before trying to open
        '''
        fname = 'testnew.dss'
        if os.path.exists(fname):
            os.remove(fname)
        with pyhecdss.DSSFile(fname, create_new=True) as d:
            d.close()
        assert os.path.exists(fname)
        with pytest.raises(FileNotFoundError):
            fname2 = 'no_such_dir/testnew.dss'
            d = pyhecdss.DSSFile(fname2)
            d.close()

    def test_num_values_in_interval(self):
        fname = 'testnew.dss'
        if os.path.exists(fname):
            os.remove(fname)
        with pyhecdss.DSSFile(fname, create_new=True) as d:
            d.close()
        # only checking if values are greater than expected, HECLIB will return the exact number of values found
        assert DSSFile.num_values_in_interval('01JAN2000', '01FEB2000', '1DAY') > 31
        assert DSSFile.num_values_in_interval('01JAN2000', '01FEB2000', '1MON') > 1
        assert DSSFile.num_values_in_interval('01JAN2000', '01FEB2000', '1YEAR') > 0


if __name__ == '__main__':
    unittest.main()
