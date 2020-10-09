import unittest
from pyhecdss import pyheclib


class TestPyHeclibBasic(unittest.TestCase):
    def test_open_close(self):
        ifltab = pyheclib.intArray(600)
        fname = "test1.dss"
        istat = pyheclib.hec_zopen(ifltab, fname)
        self.assertEqual(istat, 0)
        pyheclib.zclose_(ifltab)


#
if __name__ == '__main__':
    unittest.main()
