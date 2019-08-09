import unittest
import pyhecdss
class TestPyDsUtilsBasic(unittest.TestCase):
    def test_open_close(self):
        fname="test1.dss"
        dssfile = pyhecdss.DSSFile(fname)
        dssfile.open()
        dssfile.close()
    def test_catalog(self):
        fname="test1.dss"
        dssfile=pyhecdss.DSSFile(fname)
        dssfile.catalog()
    def test_read_ts(self):
        fname="test1.dss"
        dssfile=pyhecdss.DSSFile(fname)
        pathname='/HYDRO/1_UPSTREAM/FLOW/01DEC1989 - 01JAN1990/30MIN/HISTORICAL_V81/'
        sdate='01DEC1989'
        edate='31JAN1990'
        values,units,periodtype=dssfile.read_rts(pathname,sdate,edate)
        print(units,periodtype)
        print(values)
if __name__ == '__main__':
    unittest.main()
