'''
Tests helper function
'''
import pytest
import pyhecdss
@pytest.mark.parametrize("pathname", ["//SIN/////","/SAMPLE/SIN/////","///WAVE////","/SAMPLE/SIN/WAVE/01JAN1990/15MIN/SAMPLE1/"])
def test_get_rts(pathname):
    filename='test1.dss'
    matching_list=pyhecdss.get_rts(filename, pathname)
    assert len(matching_list) == 1
    #breakpoint()
    dfsin,units,ptype=matching_list[0]
    assert len(dfsin) > 10
@pytest.mark.parametrize("pathname", ["//S.*/////","/S.*PLE/S.*N/////","///WAV.*////","/SAMPLE/SIN/WAVE/01JAN1990/15MIN/SAMPLE1/"])
def test_get_matching_rts(pathname):
    filename='test1.dss'
    matching_list=pyhecdss.get_matching_rts(filename, pathname)
    assert len(matching_list) == 1
    #breakpoint()
    dfsin,units,ptype=matching_list[0]
    assert len(dfsin) > 10

    

