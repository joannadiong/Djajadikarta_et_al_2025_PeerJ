import pytest
import pandas as pd
import numpy as np

from bin.proc import _normalise, _difference, _predict

@pytest.fixture
def gen_df():
    id = np.ones(7)
    time = np.array([-30, 0, 15, 30, 60, 90, 120])
    var = np.array([78.602, 86.084, 67.07, 54.19, 51.56, 48.57, 51.01]) # id 1, sess 0, VA
    df = pd.DataFrame({'id': id, 'time': time, 'va': var})
    return df

@pytest.fixture
def gen_order(order=3):
    return order


def test_normalise(gen_df):
    df = gen_df # Don't run this step if testing outside function; returns function object
    actual = _normalise(df, 'va')

    baseline = df.va.values[0]
    expected = df.va.values / baseline * 100

    # use Numpy or Pandas assert functions
    np.testing.assert_array_equal(actual, expected)

def test_difference(gen_df):
    df = gen_df
    actual = _difference(df, 'va')

    baseline = df.va.values[0]
    expected = df.va.values - baseline

    # use Numpy or Pandas assert functions
    np.testing.assert_array_equal(actual, expected)

def test_predict(gen_df, gen_order):
    df = gen_df
    order = gen_order
    time = df.time[2:].values
    vals = df.va[2:].values
    actual = _predict(time, vals, order)

    # calc expected, keep non-missing values
    idx = np.isfinite(time) & np.isfinite(vals)
    if order == 1:
        coef = np.polyfit(time[idx], vals[idx], 1)
    elif order == 2:
        coef = np.polyfit(time[idx], vals[idx], 2)
    elif order == 3:
        coef = np.polyfit(time[idx], vals[idx], 3)
    elif order == 4:
        coef = np.polyfit(time[idx], vals[idx], 4)
    pred_time = np.arange(time[0], time[-1], 0.1)
    pred_vals = []
    for t in pred_time:
        if order == 1:
            v = (coef[0] * t) + coef[1]
        elif order == 2:
            v = (coef[0] * t ** 2) + (coef[1] * t) + coef[2]
        elif order == 3:
            v = (coef[0] * t ** 3) + (coef[1] * t ** 2) + (coef[2] * t) + coef[3]
        elif order == 4:
            v = (coef[0] * t ** 4) + (coef[1] * t ** 3) + (coef[2] * t ** 2) + (coef[3] * t) + coef[4]
        pred_vals.append(v)
    expected = (pred_time, pred_vals)

    np.testing.assert_array_equal(actual, expected)
