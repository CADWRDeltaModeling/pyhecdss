import unittest
import pyheclib
class TestPyHeclibBasic(unittest.TestCase):
    def test_open_close(self):
        ifltab=pyheclib.intArray(600)
        istat=pyheclib.new_intp()
        fname="test1.dss"
        pyheclib.zopen_(ifltab,fname,istat,len(fname))
        pyheclib.zclose_(ifltab)
#
if __name__ == '__main__':
    unittest.main()
