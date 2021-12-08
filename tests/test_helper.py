'''
Tests helper function
'''
import pytest
import pyhecdss


@pytest.mark.parametrize("pathname", ["//SIN/////", "/SAMPLE/SIN/////", "///WAVE////", "/SAMPLE/SIN/WAVE/01JAN1990/15MIN/SAMPLE1/","///wAvE////"])
def test_get_rts(pathname):
    filename = 'test1.dss'
    matching_list = list(pyhecdss.get_ts(filename, pathname))
    assert len(matching_list) == 1
    dfsin, units, ptype = matching_list[0]
    assert len(dfsin) > 10


@pytest.mark.parametrize("pathname", ["//S.*/////", "/S.*PLE/S.*N/////", "///WAV.*////", "/SAMPLE/SIN/WAVE/01JAN1990/15MIN/SAMPLE1/", "/saMpLE/sIn/w.*e////"])
def test_get_matching_rts(pathname):
    filename = 'test1.dss'
    matching_list = list(pyhecdss.get_matching_ts(filename, pathname))
    assert len(matching_list) == 1
    dfsin, units, ptype = matching_list[0]
    assert len(dfsin) > 10


@pytest.mark.parametrize("pathname", ["/////IR-YEAR//", ])
def test_get_ts(pathname):
    filename = 'test1.dss'
    matching_list = list(pyhecdss.get_ts(filename, pathname))
    assert len(matching_list) == 2
    dfsin, units, ptype = matching_list[0]
    assert len(dfsin) > 1


@pytest.mark.parametrize("pathname", ["/.*//////", "//.*/////", "///.*////", "////.*///", "/////.*//", "//////.*/"])
def test_get_matching_ts(pathname):
    filename = 'test1.dss'
    matching_list = list(pyhecdss.get_matching_ts(filename, pathname))
    assert len(matching_list) == 3
    dfsin, units, ptype = matching_list[0]
    assert len(dfsin) > 1

def test_non_existent_file():
    filename='test_non_existent.dss'
    with pytest.raises(Exception):
        matching_list=list(pyhecdss.get_matching_ts(filename,'///////'))
    import os
    assert not os.path.exists(filename)
