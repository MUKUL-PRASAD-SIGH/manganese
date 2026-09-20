"""Synthetic ops generator for DATA_MODE=demo.

Availability is *persistent*: breakdown episodes last 3-10 days. Without that,
lagged availability carries no signal and the shortfall model cannot learn
equipment effects.
"""

import numpy as np
import pandas as pd


def simulate(days: pd.DatetimeIndex, plan: float, opencast: bool, seed: int) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    n = len(days)
    doy = days.dayofyear.values
    monsoon = np.exp(-((doy - 215) / 40) ** 2)
    rain = rng.gamma(0.4, 1, n) * (2 + 45 * monsoon)

    avail = np.full(n, 0.93)                                   # breakdown episodes last 3-10 days
    for i in np.where(rng.random(n) < 0.03)[0]:
        avail[i:i + rng.integers(3, 11)] -= rng.uniform(0.25, 0.5)
    avail = np.clip(avail + rng.normal(0, 0.02, n), 0.3, 1.0)

    d = pd.DataFrame({"date": days, "rain": rain, "avail": avail,
                      "blast_delay": (rng.random(n) < 0.08).astype(int)})
    soil = d.rain.ewm(alpha=0.15, adjust=False).mean() / 60
    wet = (0.35 * (soil > 0.25) + 0.25 * (d.rain.rolling(3, min_periods=1).sum() > 60)) * int(opencast)
    eff = 1 - wet - 0.6 * (1 - d.avail) - 0.15 * d.blast_delay
    d["planned"] = plan
    d["actual"] = plan * eff.clip(0.2, 1.05) * rng.normal(1, 0.05, n)
    return d
