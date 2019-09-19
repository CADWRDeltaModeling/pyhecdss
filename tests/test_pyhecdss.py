import unittest
import pytest
import pyhecdss
import numpy as np
import pandas as pd
import os
class TestPyDsUtilsBasic(unittest.TestCase):
    @classmethod
    def setupClass(cls):
        os.remove('./test_rts1.dss')
        os.remove('./test_rts1.dsc')
        os.remove('./test_rts1.dsd')
        os.remove('./test_its1.dss')
        os.remove('./test_its1.dsc')
        os.remove('./test_its1.dsd')
        os.remove('./test.dsc')
        os.remove('./test.dsd')
        os.remove('./test.dsk')
    @classmethod
    def tearDownClass(cls):
        pass
    def test_open_close(self):
        fname="test1.dss"
        dssfile = pyhecdss.DSSFile(fname)
        dssfile.open()
        dssfile.close()
    def test_catalog(self):
        fname="test1.dss"
        dssfile=pyhecdss.DSSFile(fname)
        dssfile.catalog()
        self.assertTrue(os.path.exists('test1.dsc'))
        self.assertTrue(os.path.exists('test1.dsd'))
    def test_read_ts(self):
        fname="test1.dss"
        dssfile=pyhecdss.DSSFile(fname)
        pathname='/SAMPLE/SIN/WAVE/01JAN1990/15MIN/SAMPLE1/'
        sdate='01JAN1990'
        edate='31JAN1990'
        values,units,periodtype=dssfile.read_rts(pathname,sdate,edate)
        self.assertEqual(units,'UNIT-X')
        self.assertEqual(periodtype,'INST-VAL')
        self.assertEqual(len(values['10JAN1990':'11JAN1990'].values),96*2) # 96 15 min values per day
        #get series
        vseries=values.iloc[:,0]
        self.assertTrue(abs(vseries.at['01JAN1990 0430']-(-0.42578)) < 1e-03)
    def test_write_ts(self):
        fname="test_rts1.dss"
        dssfile1=pyhecdss.DSSFile(fname)
        pathname='/TEST1/ONLY1/VANILLA//1DAY/JUST-ONES/'
        startDateStr,endDateStr='01JAN1990 0100','01JAN1991 0100'
        dtr=pd.date_range(startDateStr,endDateStr,freq='1D')
        df=pd.DataFrame(np.ones(len(dtr),'d'),index=dtr)
        cunits, ctype ='CCC', 'INST-VAL'
        dssfile2=pyhecdss.DSSFile(fname)
        dssfile2.write_rts(pathname, df, cunits, ctype)
        startDateStr="01JAN1990"
        endDateStr="01JAN1991"
        df2,cunits2,ctype2=dssfile1.read_rts(pathname,startDateStr,endDateStr)
        self.assertEqual(ctype, ctype2)
        self.assertEqual(cunits, cunits2)
        self.assertEqual(1,df.iloc[0,0])
    def test_read_its(self):
        fname="test1.dss"
        dssfile=pyhecdss.DSSFile(fname)
        pathname='/SAMPLE/ITS1/RANDOM/01JAN1990 - 01JAN1992/IR-YEAR/SAMPLE2/'
        values,units,periodtype=dssfile.read_its(pathname)
        self.assertEqual(units,'YYY')
        self.assertEqual(periodtype,'INST-VAL')
        self.assertEqual(len(values),3)
        #get series
        vseries=values.iloc[:,0]
        self.assertTrue(abs(vseries.at['01JAN1990 0317']-1.5) < 1e-03)
        self.assertTrue(abs(vseries.at['05SEP1992 2349']-2.7) < 1e-03)
    def test_write_its(self):
        fname="test1.dss"
        dssfile1=pyhecdss.DSSFile(fname)
        pathname='/TEST/ITS1/VANILLA//IR-YEAR/RANDOM/'
        ta=pd.to_datetime(['01apr1990','05nov1991','07apr1997'])
        df=pd.DataFrame([0.5,0.6,0.7],index=ta,columns=["random"])
        cunits, ctype ='CCC', 'INST-VAL'
        dssfile2=pyhecdss.DSSFile(fname)
        dssfile2.write_its(pathname, df, cunits, ctype)
        df2,cunits2,ctype2=dssfile1.read_its(pathname, "01JAN1990", "01JAN1998")
        self.assertEqual(ctype, ctype2)
        self.assertEqual(cunits, cunits2)
        self.assertEqual(df2.iloc[0,0],df.iloc[0,0])
        self.assertEqual(df2.iloc[1,0],df.iloc[1,0])
        self.assertEqual(df2.iloc[2,0],df.iloc[2,0])
    def test_read_catalog(self):
        fname="test1.dss"
        dssfile=pyhecdss.DSSFile(fname)
        df = dssfile.read_catalog()
        self.assertTrue(len(df) >= 1)
    def test_get_pathnames(self):
        fname="test1.dss"
        dssfile=pyhecdss.DSSFile(fname)
        pathnames=dssfile.get_pathnames()
        self.assertTrue(len(pathnames)>0)
    def test_version(self):
        fname="test1.dss"
        cver,iver=pyhecdss.get_version(fname)
        self.assertEqual(6,iver)
        self.assertEqual('6-VE',cver)
    def test_set_message_level(self):
        fname="test1.dss"
        print("No easy way to check automatically. Just look at screen and see if lot of messages are printed?")
        pyhecdss.set_message_level(10)
        d1=pyhecdss.DSSFile(fname)
        d1.close()
        print('No easy way to check automatically. Just look at screen and no DSS messages should be printed')
        pyhecdss.set_message_level(0)
        d1=pyhecdss.DSSFile(fname)
        d1.close()
    def test_except_on_bad_path(self):
        fname="test1.dss"
        dssfile=pyhecdss.DSSFile(fname)
        pathname='/SAMPLE/INVALID_MARKER/WAVE/01JAN1990/15MIN/SAMPLE1/'
        sdate='01JAN1990'
        edate='31JAN1990'
        # values,units,periodtype=dssfile.read_rts(pathname,sdate,edate)
        self.assertRaises(RuntimeError, dssfile.read_rts, pathname, sdate, edate)

    def test_missing_dir(self):
        '''
        missing directory in filename causes crash. So check before trying to open
        '''
        fname='testnew.dss'
        if os.path.exists(fname):
            os.remove(fname)
        d=pyhecdss.DSSFile(fname)
        d.close()
        assert os.path.exists(fname)
        with pytest.raises(FileNotFoundError):
            fname2='no_such_dir/testnew.dss'
            d=pyhecdss.DSSFile(fname2)
            d.close()
    

if __name__ == '__main__':
    unittest.main()
