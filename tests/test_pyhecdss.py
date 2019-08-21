import unittest
import pyhecdss
import numpy as np
import os
class TestPyDsUtilsBasic(unittest.TestCase):
    @classmethod
    def setupClass(cls):
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
        pathname='/HYDRO/1_UPSTREAM/FLOW/01DEC1989 - 01JAN1990/30MIN/HISTORICAL_V81/'
        sdate='30DEC1989'
        edate='31JAN1990'
        values,units,periodtype=dssfile.read_rts(pathname,sdate,edate)
        self.assertEqual(units,'CFS')
        self.assertEqual(periodtype,'INST-VAL')
        self.assertEqual(len(values['10JAN1990':'11JAN1990'].values),48*2)
        #get series
        vseries=values.iloc[:,0]
        self.assertTrue(abs(vseries.at['01JAN1990 0430']-1215.6314) < 1e-03)
    def test_read_catalog(self):
        fname="test1.dss"
        dssfile=pyhecdss.DSSFile(fname)
        df = dssfile.read_catalog()
        self.assertTrue(len(df) == 1)
    def test_get_pathnames(self):
        fname="test1.dss"
        dssfile=pyhecdss.DSSFile(fname)
        pathnames=dssfile.get_pathnames()
        self.assertTrue(len(pathnames)>0)
if __name__ == '__main__':
    unittest.main()
