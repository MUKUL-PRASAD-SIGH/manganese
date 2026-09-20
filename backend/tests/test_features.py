import pandas as pd

from app.ml.features import FEATS, build_features


def test_future_rows_use_persistence():
    n_known, n_fut = 30, 10
    df = pd.DataFrame({
        "date": pd.date_range("2026-01-01", periods=n_known + n_fut), "rain": 1.0,
        "avail": [0.9] * n_known + [None] * n_fut, "breakdown": [0] * n_known + [None] * n_fut,
        "blast_delay": [0] * n_known + [None] * n_fut, "planned": 1000.0,
        "actual": [900.0] * n_known + [None] * n_fut})
    f = build_features(df, True)
    assert set(FEATS) <= set(f.columns)
    assert f.loc[35, "avail_1"] == 0.9


def test_rolling_windows_are_causal():
    """Ops features must be shifted: today's availability may not leak into today's row."""
    df = pd.DataFrame({
        "date": pd.date_range("2026-01-01", periods=10), "rain": 0.0,
        "avail": [1.0] * 9 + [0.0], "breakdown": [0] * 9 + [1],
        "blast_delay": 0, "planned": 1000.0, "actual": 1000.0})
    f = build_features(df, False)
    assert f.loc[9, "avail_1"] == 1.0          # the crash on day 9 is not visible on day 9
    assert f.loc[9, "bd_30"] == 0.0
