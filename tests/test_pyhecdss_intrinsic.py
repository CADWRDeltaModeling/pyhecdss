#Tests intrinsic functions of pyhecdss
import pytest
import pandas as pd
import numpy as np
import pyhecdss
def test_number_between():
    assert pyhecdss.DSSFile._number_between('01JAN2000','01FEB2000',delta=pd.to_timedelta(1,'D')) > 31
    assert pyhecdss.DSSFile._number_between('01JAN2000','01FEB2000',delta=np.timedelta64(1,'M')) > 1
    assert pyhecdss.DSSFile._number_between('01JAN2000','01FEB2000',delta=np.timedelta64(1,'Y')) > 0
