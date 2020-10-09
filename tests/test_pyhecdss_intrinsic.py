# Tests intrinsic functions of pyhecdss
import pytest
import pandas as pd
import numpy as np
import pyhecdss
from datetime import timedelta


def test_number_between():
    assert pyhecdss.DSSFile._number_between('01JAN2000', '01FEB2000', delta=timedelta(days=1)) > 31
    assert pyhecdss.DSSFile._number_between('01JAN2000', '01FEB2000', delta=timedelta(days=28)) > 1
    assert pyhecdss.DSSFile._number_between('01JAN2000', '01FEB2000', delta=timedelta(days=365)) > 0
