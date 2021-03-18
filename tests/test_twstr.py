'''
Tests timewindow str parsing
'''
import pytest
import pyhecdss


@pytest.mark.parametrize('twstr,sdate,edate',
                         [
                             ('01jan1990 0000 - 05feb1991 0000', '01JAN1990', '05FEB1991'),
                             ('05/01/2002 - 03/25/2003','01MAY2002','25MAR2003'),
                             ('01OCT2001 0000 - 01OCT2012 0000','01OCT2001','01OCT2012')
                         ]
                         )
def test_twstr(twstr, sdate, edate):
    sd, ed = pyhecdss.get_start_end_dates(twstr)
    assert sdate == sd
    assert edate == ed
